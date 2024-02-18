#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IngestLogReason(str, Enum):
    """
    Ingest Log Reasons.
    """

    ok = "ok"
    metadata_extract_issue = "metadata extraction issue"
    updated = "updated"
    already_exists = "already exists"


class IngestLogStatus(str, Enum):
    """
    Ingest Log Statuses.
    """

    ok = "ok"
    fail = "fail"
    issue = "issue"


class IngestLogBase(BaseModel):
    """
    Ingest Log.
    """

    batchid: str = None  # ingest batch-id (YYYY-MM-DD_HHMMSS.nnnn) used to group an ingest log set.
    source: str = None  # source
    status: IngestLogStatus = None  # ok, fail, etc.
    reason: Optional[IngestLogReason] = None  # metadata_issue
    message: Optional[str] = None  # metadata extraction failed with error: xxxx


class IngestLog(IngestLogBase):
    """
    Extended (added by backend logic)
    """

    # note: this needs to be set/overwrote on result instantiation as using
    #  datetime.now() here will only get you now of when worker was started.
    created: datetime = datetime.now()
    updated: datetime = datetime.now()

    creator: Optional[str] = None
    updator: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.timestamp()}


class IngestResultType(str, Enum):
    """
    Ingest Result types.
    """

    ok = "ok, processed successfully"
    updated = "document updated"
    fail_exists = "failure, document already exists"
    extract_metadata_issue = "extract metadata issue"
