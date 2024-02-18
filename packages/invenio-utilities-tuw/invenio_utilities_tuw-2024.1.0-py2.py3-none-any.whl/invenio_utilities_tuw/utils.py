# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utility functions for Invenio-Utilities-TUW."""

from difflib import SequenceMatcher

from flask import current_app
from invenio_access.permissions import any_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_rdm_records.proxies import current_rdm_records
from werkzeug.utils import import_string


def get_or_import(value, default=None):
    """Try an import if value is an endpoint string, or return value itself."""
    if isinstance(value, str):
        return import_string(value)
    elif value:
        return value

    return default


def get_record_service():
    """Get the configured RecordService."""
    factory = current_app.config.get("UTILITIES_TUW_RECORD_SERVICE_FACTORY", None)

    if factory is not None:
        factory = get_or_import(factory)
    else:
        factory = lambda: current_rdm_records.records_service

    return factory()


def get_user_by_identifier(id_or_email):
    """Get the user specified via email or ID."""
    if id_or_email is not None:
        # note: this seems like the canonical way to go
        #       'id_or_email' can be either an integer (id) or email address
        u = current_accounts.datastore.get_user(id_or_email)
        if u is not None:
            return u
        else:
            raise LookupError("user not found: %s" % id_or_email)

    raise ValueError("id_or_email cannot be None")


def get_identity_for_user(user):
    """Get the Identity for the user specified via email or ID."""
    if user is not None:
        found_user = get_user_by_identifier(user)
        identity = get_identity(found_user)
        identity.provides.add(any_user)
        return identity

    return system_identity


def similarity(a: str, b: str) -> float:
    """Calculate the similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()
