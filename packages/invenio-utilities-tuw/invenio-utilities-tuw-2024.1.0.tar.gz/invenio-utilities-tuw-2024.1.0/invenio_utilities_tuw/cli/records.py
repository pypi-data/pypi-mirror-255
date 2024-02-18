# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for records."""

import json
import sys

import click
from flask.cli import with_appcontext
from invenio_db import db
from invenio_records_resources.services.errors import PermissionDeniedError

from ..utils import get_identity_for_user, get_record_service, get_user_by_identifier
from .options import (
    option_as_user,
    option_owners,
    option_pid_type,
    option_pid_value,
    option_pid_values,
    option_pretty_print,
    option_raw,
)
from .utils import convert_to_recid, get_object_uuid, patch_metadata, set_record_owners


@click.group()
def records():
    """Management commands for records."""


@records.command("list")
@option_as_user
@with_appcontext
def list_records(user):
    """List all records accessible to the given user."""
    identity = get_identity_for_user(user)
    service = get_record_service()
    rec_model_cls = service.record_cls.model_cls

    recids = [
        rec.json["id"]
        for rec in rec_model_cls.query
        if rec is not None and rec.json is not None
    ]

    for recid in recids:
        try:
            rec = service.read(id_=recid, identity=identity)
            recid = rec.id
            title = rec.data["metadata"].get("title", "-")
            files = rec._record.files
            if files.enabled:
                num_files = f"{len(files.entries):02}"
            else:
                num_files = "no"

            click.secho(f"{recid}\t{num_files} files\t{title}", fg="green")
        except PermissionDeniedError:
            pass


@records.command("show")
@option_pid_value
@option_pid_type
@option_as_user
@option_pretty_print
@option_raw
@with_appcontext
def show_record(pid, pid_type, user, pretty_print, raw):
    """Show the stored data for the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    indent = 2 if pretty_print else None

    record = service.read(id_=pid, identity=identity)
    data = record._record.model.json if raw else record.data
    data = json.dumps(data, indent=indent)

    click.echo(data)


@records.command("update")
@click.argument("metadata_file", type=click.File("r"))
@option_pid_value
@option_pid_type
@option_as_user
@click.option(
    "--patch/--replace",
    "-P/-R",
    default=False,
    help=(
        "replace the record's metadata entirely, or leave unmentioned fields as-is "
        "(default: replace)"
    ),
)
@click.option(
    "--direct",
    "-d",
    default=False,
    is_flag=True,
    help=(
        "circumvent the record service, and thus permission checks, "
        "and update the record directly (not recommended)"
    ),
)
@option_owners
@with_appcontext
def update_record(metadata_file, pid, pid_type, user, patch, owners, direct):
    """Update the specified draft's metadata."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    metadata = json.load(metadata_file)

    if patch:
        record_data = service.read(id_=pid, identity=identity).data.copy()
        metadata = patch_metadata(record_data, metadata)

    if direct:
        record = service.read(id_=pid, identity=identity)._record
        record.update(metadata)

        # the refresh is required because the access system field takes precedence
        # over the record's data in 'record.commit()'
        record.access.refresh_from_dict(record["access"])
        record.commit()
        db.session.commit()
        service.indexer.index(record)

    else:
        try:
            # first, try the modern approach of updating records (March 2021)
            service.edit(id_=pid, identity=identity)
            service.update_draft(id_=pid, identity=identity, data=metadata)
            service.publish(id_=pid, identity=identity)

        except Exception as e:
            # if that fails, try the good old plain update
            click.secho(f"error: {e}", fg="yellow", err=True)
            click.secho("trying with service.update()...", fg="yellow", err=True)
            service.update(id_=pid, identity=identity, data=metadata)

    if owners:
        record = service.read(id_=pid, identity=identity)._record
        owners = [get_user_by_identifier(owner) for owner in owners]
        set_record_owners(record, owners)
        if service.indexer:
            service.indexer.index(record)

    click.secho(pid, fg="green")


@records.command("delete")
@click.confirmation_option(prompt="are you sure you want to delete this record?")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def delete_record(pid, pid_type, user):
    """Delete the specified record."""
    identity = get_identity_for_user(user)
    recid = convert_to_recid(pid, pid_type)
    service = get_record_service()
    service.delete(id_=recid, identity=identity)

    click.secho(recid, fg="red")


@records.group()
def files():
    """Manage files deposited with the record."""


@files.command("list")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def list_files(pid, pid_type, user):
    """Show a list of files deposited with the record."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    record = service.read(id_=recid, identity=identity)._record

    for name, rec_file in record.files.entries.items():
        fi = rec_file.file
        if fi:
            click.secho(f"{name}\t{fi.uri}\t{fi.checksum}", fg="green")
        else:
            click.secho(name, fg="red")


@files.command("verify")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def verify_files(pid, pid_type, user):
    """Verify the checksums for each of the record's files."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    record = service.read(id_=recid, identity=identity)._record
    num_errors = 0

    for name, rec_file in record.files.entries.items():
        if not rec_file.file:
            click.secho(name, fg="red")

        elif rec_file.file.verify_checksum():
            click.secho(name, fg="green")

        else:
            click.secho(f"{name}: failed checksum verification", fg="yellow", err=True)
            num_errors += 1

    # persist the 'last_check_at' timestamp for each file
    db.session.commit()

    if num_errors > 0:
        click.secho(
            f"{num_errors} files failed the checksum verification",
            fg="yellow",
            err=True,
        )
        sys.exit(1)


@records.command("reindex")
@option_pid_values
@option_pid_type
@with_appcontext
def reindex_records(pids, pid_type):
    """Reindex all available (or just the specified) records."""
    service = get_record_service()

    if pids:
        records = [
            service.record_cls.get_record(get_object_uuid(pid, pid_type))
            for pid in pids
        ]
    else:
        records = [
            service.record_cls.get_record(meta.id)
            for meta in service.record_cls.model_cls.query
            if meta is not None and meta.json is not None
        ]

    for record in records:
        service.indexer.index(record)
