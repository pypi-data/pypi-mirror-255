#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

from typing import List

from pydantic import BaseModel


class UserConfigDefaults(BaseModel):
    """
    Defaults for UserConfig.
    """

    source: str = None
    user: str = None
    base: str = None


class UserConfigIngest(BaseModel):
    """
    User Config Ingest.
    """

    file_types: List[str] = None


class UserConfigDatabase(BaseModel):
    """
    User Config database info.
    """

    db_uri: str = None


class UserConfigBase(BaseModel):
    """
    User config base.
    """

    player: str = None
    use_pager: bool = False

    database: UserConfigDatabase = None
    defaults: UserConfigDefaults = None
    ingest: UserConfigIngest = None
    source_mappings: dict = None
