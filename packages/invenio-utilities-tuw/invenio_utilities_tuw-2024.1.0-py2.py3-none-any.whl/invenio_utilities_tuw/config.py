# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Configuration for Invenio-Utilities-TUW."""

from invenio_rdm_records.proxies import current_rdm_records

UTILITIES_TUW_RECORD_SERVICE_FACTORY = lambda: current_rdm_records.records_service
"""Factory function for creating a RecordService."""
