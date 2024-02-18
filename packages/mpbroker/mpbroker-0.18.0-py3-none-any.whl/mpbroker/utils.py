#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

import json
import subprocess  # nosec
import time
from operator import itemgetter
from pathlib import Path
from typing import List

import click
import pycouchdb
import requests
import typer
from natsort import natsorted
from rich import box
from rich.table import Table

from mpbroker.config.config import user_cfg
from mpbroker.models.media import (
    MediaMetadata,
    MediaPlayHistory,
    MediaPlayRating,
    MediaPlayStatus,
)

server = pycouchdb.Server(user_cfg.database.db_uri)


def db_not_available(location=None):
    """
    Database is not available: display message and exit.
    """

    _loc = f" ({location})"

    typer.secho(
        f"\nDatabase unavailable{_loc}, is it up?",
        fg=typer.colors.RED,
        bold=True,
        err=True,
    )
    raise typer.Exit()


def determine_status_from_flags(
    new: bool = False,
    played: bool = False,
    watched: bool = False,
):
    """
    Determine the status from status flags.
    @return: status to show or None (indicating no filter on status)
    @raises: error if more than one flag set.
    """

    _status = []
    if new:
        _status.append(MediaPlayStatus.new.value)
    if played:
        _status.append(MediaPlayStatus.played.value)
    if watched:
        _status.append(MediaPlayStatus.watched.value)
    if len(_status) < 1:
        return None
    elif len(_status) > 1:
        typer.secho(
            f"Too many status filter flags: {_status}!",
            fg=typer.colors.RED,
            bold=True,
            err=True,
        )
        typer.echo(
            "You can only supply one status to filter on.",
        )
        raise typer.Exit()
    else:
        return _status[0]


def dprint(data):
    """
    Pretty print a dict/list of dicts.
    """

    import pprint

    pprint.pprint(data, compact=True)


def get_sources_paths(sources: List):
    """
    Get sources paths.
    NOTE: source paths are validated (checked), if a path is invalid (does not exist)
          it will not be returned.
    @return: list of source paths.
    """

    _ret = []
    for source in sources:
        # ~ typer.echo(f"   ─⏵ checking source: {source}")
        if source in user_cfg.source_mappings:
            _path = user_cfg.source_mappings[source]
            # check if path exists.
            if Path(_path).is_dir() and any(Path(_path).iterdir()):
                # ~ typer.echo(f"- found {_path} and it has data...")
                _ret.append({"source": source, "path": _path})
            # ~ typer.echo(f"- found {source} in source_mappings: {user_cfg.source_mappings[source]}")

    return _ret


def extract_metadata(filepath) -> MediaMetadata:
    """
    Extract media metadata from a file
    """

    from pymediainfo import MediaInfo

    try:
        media_info = MediaInfo.parse(filepath)

        # extract metadata
        metadata = MediaMetadata(
            file_size=media_info.tracks[0].other_file_size[0],
            file_type=media_info.tracks[1].internet_media_type,
            file_format=media_info.tracks[0].format,
            encoding=media_info.tracks[1].encoded_library_name,
            duration=media_info.tracks[0].other_duration[0],
            resolution=f"{media_info.tracks[1].width} x {media_info.tracks[1].height}",
            aspect_ratio=media_info.tracks[1].other_display_aspect_ratio[0],
            audio_format=media_info.tracks[2].format,
            audio_sampling=media_info.tracks[2].sampling_rate,
        )
    except Exception as e:
        return None, f"Failed extracting metadata for {filepath} with error: {e}"

    return metadata, None


def generate_sid(instr: str = None):
    """
    Generate a sid given an input string.
    Example: 'Duck_Dynasty_S1_D1.mkv' ─⏵ 'DCKDNSTS1D1.MKV'
    """

    return instr.translate(str.maketrans("", "", "AaEeIiOoUuYy_-()[]")).upper()


def jprint(data: str = None):
    """
    JSON pretty print a string.
    """

    # typer.echo(f"- data ({type(data)}): {data}")
    _data = json.loads(data)
    typer.echo(json.dumps(_data, indent=4, sort_keys=True))


def make_doc(doc=None, rename_doc_id: bool = False):
    """
    Create a couchdb doc by deserializing the class to json, loading it back to
    json and finally renaming the doc_id field to _id.

    NOTE: the double deserialization is needed to get dates deserialized (easily)
    NOTE: we need to rename doc_id to _id as we can name it _id in the model or alias
          it as python treats it as a local and does not export it on deserialization.
    """

    j = json.loads(doc.json())
    if "doc_id" in j and rename_doc_id:
        j["_id"] = j.pop("doc_id")

    return j


def play_item(doc=None, name: str = None, user: str = None):
    """
    Play an item.
    """

    db = server.database("media")
    try:
        # ~ typer.echo(f"- playing doc: {doc}")
        # typer.echo(f">> source_mappings: {user_cfg.source_mappings}")
        source_paths = get_sources_paths(doc["sources"])
        _name = f"{doc['directory']}/{doc['name']}"
        if len(source_paths) < 1:
            typer.echo(
                f"No viable sources found for {_name} with sources: {doc['sources']}"
            )
            raise typer.Exit()
        # typer.echo(f" source_paths: {source_paths}")

        # @TODO: currently we simply play the first source_path - should have something
        #  better here eventually like a ranking or some checking.
        _media_path = f"{source_paths[0]['path']}/{_name}"

        # capture when we start playing.
        _start = time.time()

        # @TODO: check if file and player exist, then execute
        subprocess.call([user_cfg.player, _media_path])  # nosec
        _end = time.time()

        # create the play history.
        _new_history = MediaPlayHistory(
            base=source_paths[0]["path"],
            player=user_cfg.player,
            start=_start,
            end=_end,
            client=f"{user}",
        )
        _history = []
        if (
            "play" in doc
            and "history" in doc["play"]
            and doc["play"]["history"]
            and len(doc["play"]["history"]) > 0
        ):
            _history = doc["play"]["history"]

        _history.append(json.loads(_new_history.json()))
        doc["play"]["history"] = _history

        # post-play updates from user
        doc["play"]["status"] = typer.prompt(
            "update Play Status",
            default=MediaPlayStatus.played.value,
            type=click.Choice([str(i) for i in MediaPlayStatus._value2member_map_]),
        )
        doc["play"]["rating"] = int(
            typer.prompt(
                "Rate item",
                default=MediaPlayRating.ok.value,
                type=click.Choice([str(i) for i in MediaPlayRating._value2member_map_]),
            )
        )
        rating_notes = typer.prompt(
            "Add Rating notes? (leave blank to not add a note)",
            default="",
            show_default=False,
        )
        if rating_notes:
            doc["play"]["rating_notes"] = rating_notes

        notes = typer.prompt(
            "Add Notes for media item? (leave blank to not add a note update)\n  A note for the media item could be something specific like 'watched Ep 1, 2, and 4'",
            default="",
            show_default=False,
        )
        if notes:
            doc["play"]["notes"] = notes

        db.save(doc)

    except requests.exceptions.ConnectionError:
        db_not_available("play_item")
    except pycouchdb.exceptions.NotFound:
        typer.secho(
            f"Media item {_name} not found for user {user}.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit()


def results_by_name(
    name: str, user: str, status: str = None, fdirectory: str = "", fsource: str = None
):
    """
    Get Results from a given Name.
    """

    _name = f"{user}:{name}"
    _status = f"-{status}" if status else ""

    try:
        db = server.database("media")
        results = db.query(
            f"filters/by-name{_status}",
            startkey=_name,
            endkey=f"{_name}\ufff0",
            as_list=True,
        )
        if results:
            # post process results.
            if fdirectory or fsource:
                _results = []
                for item in results:
                    # ~ typer.secho(f">>> item={item}", fg=typer.colors.YELLOW, bold=True)
                    # if both filters are supplied we must match on both to add to results
                    if fdirectory and fsource:
                        if (
                            item["value"][0]
                            and len(item["value"][5]) > 0
                            and fdirectory in item["value"][0]
                            and fsource in item["value"][5]
                        ):
                            _results.append(item)
                    elif fdirectory:
                        if item["value"][0] and fdirectory in item["value"][0]:
                            _results.append(item)
                    elif fsource:
                        if len(item["value"][5]) > 0 and fsource in item["value"][5]:
                            _results.append(item)
                    # ~ else:
                    # ~ typer.secho(f">>> NO FILTER MATCHES for item={item}", fg=typer.colors.BLUE, bold=True)

                if len(_results) > 0:
                    return _results
                else:
                    typer.secho("No results found", fg=typer.colors.MAGENTA, bold=True)
                    raise typer.Exit()

            return results
        else:
            typer.secho("No results found", fg=typer.colors.MAGENTA, bold=True)
            raise typer.Exit()
    except requests.exceptions.ConnectionError:
        db_not_available("results_by_name")


def results_to_table(
    results=None, name: str = None, user: str = None, directory: str = None
):
    """
    Make query results into a [rich] table for display.
    """

    _directory_label = f" in '{directory}'" if directory else ""
    _caption = typer.style(
        f"{len(results)} items found for term '{name}'{_directory_label}",
        fg=typer.colors.MAGENTA,
        bold=False,
    )
    table = Table(
        box=box.ROUNDED,
        show_lines=False,
        caption=_caption,
        collapse_padding=True,
        pad_edge=False,
        padding=0,
        show_edge=True,
        leading=0,
        header_style="bold magenta",
    )
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")
    table.add_column("Rating")
    table.add_column("Notes")
    table.add_column("Sources", justify="right", style="yellow")
    table.add_column("Length")

    for item in natsorted(results, key=itemgetter(*["id"])):
        _status = item["value"][1]
        _rating = f"{item['value'][2]}" if item["value"][2] else ""
        _rating = f"{_rating} {item['value'][3]}" if item["value"][3] else _rating
        _notes = f"{item['value'][4]}" if item["value"][4] else ""
        _duration = f"{item['value'][6]}" if item["value"][6] else ""
        # ~ typer.echo(f" - {item['value'][0]}/{item['key']} | {_status} {_rating}")
        _user = f"{user}:"
        table.add_row(
            f"{item['value'][0]}/{item['key'].replace(_user, '')}",
            _status,
            _rating,
            _notes,
            f"{', '.join(item['value'][5])}",
            _duration,
        )
    return table
