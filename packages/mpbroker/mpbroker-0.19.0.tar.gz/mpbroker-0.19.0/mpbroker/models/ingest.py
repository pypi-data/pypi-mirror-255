#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IngestSummary(BaseModel):
    processed: int = 0
    added: int = 0
    updated: int = 0
    exists: int = 0
    issue_find: int = 0
    issue_mex: int = 0


class IngestIssueKind(str, Enum):
    connection_error = "ConnectionError"
    metadata_extraction_error = "MetadataExtractionError"


class IngestMetadataType(str, Enum):
    none = "none"
    new = "new"
    update = "update"
    both = "both"


class IngestIssue(BaseModel):
    kind: IngestIssueKind | None
    message: str | None
