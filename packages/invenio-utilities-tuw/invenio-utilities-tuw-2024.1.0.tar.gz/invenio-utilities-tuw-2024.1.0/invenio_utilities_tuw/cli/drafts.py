# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for drafts."""

import json
import os
import sys
from os.path import basename, isdir, isfile, join

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.errors import PermissionDeniedError

from ..utils import get_identity_for_user, get_record_service, get_user_by_identifier
from .options import (
    option_as_user,
    option_owners,
    option_pid_type,
    option_pid_value,
    option_pretty_print,
    option_raw,
    option_vanity_pid,
)
from .utils import (
    convert_to_recid,
    create_record_from_metadata,
    patch_metadata,
    read_metadata,
    set_record_owners,
)


def auto_increase_bucket_limits(bucket, filepaths, to_unlimited=False):
    """Dynamically increase the bucket quoat if necessary."""
    # see what the file sizes look like
    file_sizes = [os.path.getsize(filepath) for filepath in filepaths]
    sum_sizes = sum(file_sizes)
    max_size = max(file_sizes)

    if bucket.quota_left is not None:
        if to_unlimited:
            bucket.quota_size = None

        else:
            # see how big the files are, and compare it against the bucket's quota
            req_extra_quota = sum_sizes - bucket.quota_left

            # if we need some extra quota, increase it
            if req_extra_quota > 0:
                bucket.quota_size += req_extra_quota

    if bucket.max_file_size and bucket.max_file_size < max_size:
        # do similar checks for the maximum file size
        if to_unlimited:
            bucket.max_file_size = None
        else:
            bucket.max_file_size = max_size

    # make changes known
    db.session.flush()


@click.group()
def drafts():
    """Management commands for creation and publication of drafts."""


@drafts.command("list")
@option_as_user
@with_appcontext
def list_drafts(user):
    """List all drafts accessible to the given user."""
    identity = get_identity_for_user(user)
    service = get_record_service()
    recids = [
        dm.json["id"]
        for dm in service.draft_cls.model_cls.query.all()
        if dm is not None and dm.json is not None
    ]

    for recid in recids:
        try:
            draft = service.read_draft(id_=recid, identity=identity)
            recid = draft.id
            title = draft.data["metadata"].get("title", "-")
            files = draft._record.files
            if files.enabled:
                num_files = f"{len(files.entries):02}"
            else:
                num_files = "no"

            click.secho(f"{recid}\t{num_files} files\t{title}", fg="green")
        except PermissionDeniedError:
            pass


@drafts.command("create")
@click.argument("metadata_path", type=click.Path(exists=True))
@option_as_user
@click.option(
    "--publish",
    "-p",
    is_flag=True,
    default=False,
    help="publish the draft after creation (default: false)",
)
@option_owners
@option_vanity_pid
@with_appcontext
def create_draft(metadata_path, publish, user, owners, vanity_pid):
    """Create a new record draft with the specified metadata.

    The specified metadata path can either point to a JSON file containing the metadata,
    or it can point to a directory.
    In the former case, no files will be added to the created draft.
    In the latter case, it is assumed that the directory contains a file called
    "metadata.json".
    Further, all files contained in the "files/" subdirectory will be added to the
    draft, if such a subdirectory exists.
    """
    recid = None
    service = get_record_service()
    file_service = service.draft_files
    identity = get_identity_for_user(user)

    if isfile(metadata_path):
        metadata = read_metadata(metadata_path)
        draft = create_record_from_metadata(metadata, identity, vanity_pid=vanity_pid)
        recid = draft["id"]
        draft.files.enabled = False
        draft.commit()

    elif isdir(metadata_path):
        metadata_file_path = join(metadata_path, "metadata.json")
        deposit_files_path = join(metadata_path, "files")
        if not isfile(metadata_file_path):
            raise FileNotFoundError(metadata_file_path)

        metadata = read_metadata(metadata_file_path)
        draft = create_record_from_metadata(metadata, identity)
        recid = draft["id"]
        draft.files.enabled = True
        draft.commit()

        file_names = []
        file_paths = []
        if isdir(deposit_files_path):
            exists = lambda fn: isfile(join(deposit_files_path, fn))
            content = os.listdir(deposit_files_path)
            file_names = [basename(fn) for fn in content if exists(fn)]
            for fn in file_names:
                file_paths.append(join(deposit_files_path, fn))

            if len(content) != len(file_names):
                ignored = [basename(fn) for fn in content if not exists(fn)]
                msg = f"ignored in '{deposit_files_path}': {ignored}"
                click.secho(msg, fg="yellow", err=True)

        auto_increase_bucket_limits(draft.files.bucket, file_paths)
        file_service.init_files(
            id_=recid, identity=identity, data=[{"key": fn} for fn in file_names]
        )
        for fn in file_names:
            file_path = join(deposit_files_path, fn)
            with open(file_path, "rb") as deposit_file:
                file_service.set_file_content(
                    id_=recid, file_key=fn, identity=identity, stream=deposit_file
                )

            file_service.commit_file(id_=recid, file_key=fn, identity=identity)

    else:
        raise TypeError(f"neither a file nor a directory: {metadata_path}")

    if owners:
        owners = [get_user_by_identifier(owner) for owner in owners]
        set_record_owners(draft, owners)
        if service.indexer:
            service.indexer.index(draft)

    if publish:
        service.publish(id_=recid, identity=identity)

    # commit, as there are code paths that don't have a commit otherwise
    db.session.commit()
    click.secho(recid, fg="green")


@drafts.command("show")
@option_pid_value
@option_pid_type
@option_as_user
@option_pretty_print
@option_raw
@with_appcontext
def show_draft(pid, pid_type, user, pretty_print, raw):
    """Show the stored data for the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    indent = 2 if pretty_print else None

    draft = service.read_draft(id_=pid, identity=identity)
    data = draft._record.model.json if raw else draft.data
    data = json.dumps(data, indent=indent)

    click.echo(data)


@drafts.command("update")
@click.argument("metadata_file", type=click.File("r"))
@option_pid_value
@option_pid_type
@option_as_user
@click.option(
    "--patch/--replace",
    "-P/-R",
    default=False,
    help=(
        "replace the draft's metadata entirely, or leave unmentioned fields as-is "
        "(default: replace)"
    ),
)
@option_owners
@with_appcontext
def update_draft(metadata_file, pid, pid_type, user, patch, owners):
    """Update the specified draft's metadata."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    metadata = json.load(metadata_file)

    if patch:
        draft_data = service.read_draft(id_=pid, identity=identity).data.copy()
        metadata = patch_metadata(draft_data, metadata)

    if owners:
        draft = service.read_draft(id_=pid, identity=identity)._record
        owners = [get_user_by_identifier(owner) for owner in owners]
        set_record_owners(draft, owners)

    service.update_draft(id_=pid, identity=identity, data=metadata)
    click.secho(pid, fg="green")


@drafts.command("publish")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def publish_draft(pid, pid_type, user):
    """Publish the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    service.publish(id_=pid, identity=identity)

    click.secho(pid, fg="green")


@drafts.command("delete")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def delete_draft(pid, pid_type, user):
    """Delete the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    service.delete_draft(id_=pid, identity=identity)

    click.secho(pid, fg="red")


@drafts.group()
def files():
    """Manage files deposited with the draft."""


@files.command("add")
@click.argument("filepaths", metavar="PATH", type=click.Path(exists=True), nargs=-1)
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def add_files(filepaths, pid, pid_type, user):
    """Add the specified files to the draft."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    file_service = service.draft_files
    draft = service.read_draft(id_=recid, identity=identity)._record

    if not draft.files.enabled:
        draft.files.enabled = True
        draft.commit()

    paths = []
    for file_path in filepaths:
        if isdir(file_path):
            # add all files (no recursion into sub-dirs) from the directory
            exists = lambda fn: isfile(join(file_path, fn))
            content = os.listdir(file_path)
            file_names = [basename(fn) for fn in content if exists(fn)]

            if len(content) != len(file_names):
                ignored = [basename(fn) for fn in content if not exists(fn)]
                msg = f"ignored in '{file_path}': {ignored}"
                click.secho(msg, fg="yellow", err=True)

            paths_ = [join(file_path, fn) for fn in file_names]
            paths.extend(paths_)

        elif isfile(file_path):
            paths.append(file_path)

    # make sure that the files fit in the bucket, and add them
    auto_increase_bucket_limits(draft.files.bucket, paths)
    keys = [basename(fp) for fp in paths]
    if len(set(keys)) != len(keys):
        click.secho(
            "aborting: duplicates in file names detected", fg="yellow", err=True
        )
        sys.exit(1)

    # TODO: this fails if a file with the same name already exists
    file_service.init_files(
        id_=recid, identity=identity, data=[{"key": basename(fp)} for fp in paths]
    )
    for fp in paths:
        fn = basename(fp)
        with open(fp, "rb") as deposit_file:
            file_service.set_file_content(
                id_=recid, file_key=fn, identity=identity, stream=deposit_file
            )
        file_service.commit_file(id_=recid, file_key=fn, identity=identity)

    click.secho(recid, fg="green")


@files.command("remove")
@click.argument("filekeys", metavar="FILE", nargs=-1)
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def remove_files(filekeys, pid, pid_type, user):
    """Remove the given deposited files from the draft.

    Note that this operation does not remove the files from storage!
    """
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    file_service = service.draft_files

    for file_key in filekeys:
        try:
            file_service.delete_file(id_=recid, file_key=file_key, identity=identity)
            click.secho(file_key, fg="red")

        except KeyError as err:
            click.secho(f"error: {err}", fg="yellow", err=True)

    draft = service.read_draft(id_=recid, identity=identity)._record
    if not draft.files.entries:
        draft.files.enabled = False
        draft.commit()
        db.session.commit()


@files.command("list")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def list_files(pid, pid_type, user):
    """Show a list of files deposited with the draft."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service = get_record_service()
    draft = service.read_draft(id_=recid, identity=identity)._record

    for name, rec_file in draft.files.entries.items():
        fi = rec_file.file
        if fi:
            click.secho(f"{name}\t{fi.uri}\t{fi.checksum}", fg="green")
        else:
            click.secho(name, fg="red")


@files.command("verify")
@option_pid_value
@option_pid_type
@with_appcontext
def verify_files(pid, pid_type):
    """Verify the checksums for each of the draft's files."""
    recid = convert_to_recid(pid, pid_type)
    service = get_record_service()
    draft = service.read_draft(id_=recid, identity=system_identity)._record
    num_errors = 0

    for name, rec_file in draft.files.entries.items():
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
