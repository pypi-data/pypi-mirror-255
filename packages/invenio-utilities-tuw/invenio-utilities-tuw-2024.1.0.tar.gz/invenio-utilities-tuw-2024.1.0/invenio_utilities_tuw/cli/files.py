# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for files."""

import os
import sys
from collections import defaultdict

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_files_rest.models import FileInstance, Location, ObjectVersion
from sqlalchemy.exc import IntegrityError

from ..utils import get_record_service
from .options import option_pid_type, option_pid_value_optional
from .utils import convert_to_recid


def remove_file(file_path, max_rmdir_depth=3):
    """Remove the file and directories in its path that just became empty."""
    os.remove(file_path)
    path = os.path.dirname(file_path)
    depth = 0

    # only delete directories until the maximum rmdir depth is hit, or the
    # directory contains files, or we hit a permission error
    while depth < max_rmdir_depth and not os.listdir(path):
        try:
            os.rmdir(path)
        except PermissionError:
            break

        path, _ = os.path.split(path)
        depth += 1


def get_zombie_files(location):
    """Get a list of files in the given Location that aren't referenced in the DB."""
    # see which files are on disk at the given location
    all_files = []
    for p, _, files in os.walk(location.uri):
        all_files += [os.path.join(p, f) for f in files]

    # filter out those files that invenio has knowledge about
    for bucket in location.buckets:
        for obj in bucket.objects:
            if obj.file and obj.file.uri in all_files:
                # an object_version without attached file_instance
                # likely denotes a soft-deleted file
                all_files.remove(obj.file.uri)

    for file_instance in FileInstance.query.all():
        if file_instance.uri in all_files:
            all_files.remove(file_instance.uri)

    return all_files


def get_orphan_files():
    """Get a list of FileInstances that don't have associated ObjectVersions."""
    return FileInstance.query.filter(~FileInstance.objects.any()).all()


@click.group()
def files():
    """Management commands for files."""


@files.command("verify")
@click.option(
    "verify_all",
    "--all/--no-orphans",
    "-a/-A",
    default=False,
    help="Verify all files, or just ones that aren't orphaned",
)
@with_appcontext
def verify_files(verify_all):
    """Verify the checksums for all files."""
    num_errors = 0

    for file_instance in FileInstance.query.all():
        if file_instance.objects or verify_all:
            # build the display name from the file's URI and its object version keys
            aliases = ", ".join([f'"{o.key}"' for o in file_instance.objects])
            name = f"{file_instance.uri} (alias {aliases or '<N/A>'})"

            try:
                if file_instance.verify_checksum():
                    click.secho(name, fg="green")
                else:
                    click.secho(
                        f"{name}: failed checksum verification", fg="yellow", err=True
                    )
                    num_errors += 1

            except Exception as error:
                click.secho(
                    f"{name}: failed checksum verification: {error}", fg="red", err=True
                )
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


@files.group("deleted")
def deleted():
    """Management commands for soft-deleted files."""


@deleted.command("list")
@option_pid_value_optional
@option_pid_type
@with_appcontext
def list_deleted_files(pid, pid_type):
    """List files that have already been soft-deleted.

    Optionally, this operation can be restricted to the bucket associated with a draft
    (via its PID).
    """
    recid = convert_to_recid(pid, pid_type) if pid else None
    service = get_record_service()
    identity = system_identity

    # if a PID was specified, limit the cleaning to this record's bucket
    marked_as_deleted = ObjectVersion.query.filter_by(file_id=None, is_head=True)
    if recid is not None:
        draft = service.read_draft(id_=recid, identity=identity)._record
        marked_as_deleted = marked_as_deleted.filter_by(bucket=draft.files.bucket)

    # hard-delete all soft-deleted ObjectVersions
    file_instances = defaultdict(set)
    for dov in marked_as_deleted.all():
        for ov in ObjectVersion.get_versions(dov.bucket, dov.key).all():
            if ov.file is not None:
                file_instances[ov.key].add(ov.file)

    # delete the associated FileInstances, and remove files from disk
    for key in file_instances:
        for fi in file_instances[key]:
            click.secho(f"{key}\t{fi.uri}", fg="green")

    db.session.commit()


@deleted.command("clean")
@click.confirmation_option(
    prompt="Are you sure you want to permanently remove soft-deleted files?"
)
@option_pid_value_optional
@option_pid_type
@with_appcontext
def hard_delete_files(pid, pid_type):
    """Hard-delete files that have already been soft-deleted.

    Optionally, this operation can be restricted to the bucket associated with a draft
    (via its PID).
    """
    recid = convert_to_recid(pid, pid_type) if pid else None
    service = get_record_service()
    identity = system_identity

    # if a PID was specified, limit the cleaning to this record's bucket
    marked_as_deleted = ObjectVersion.query.filter_by(file_id=None, is_head=True)
    if recid is not None:
        draft = service.read_draft(id_=recid, identity=identity)._record
        marked_as_deleted = marked_as_deleted.filter_by(bucket=draft.files.bucket)

    # hard-delete all soft-deleted ObjectVersions
    file_instances = defaultdict(set)
    for dov in marked_as_deleted.all():
        for ov in ObjectVersion.get_versions(dov.bucket, dov.key).all():
            ov.remove()
            if ov.file is not None:
                file_instances[ov.key].add(ov.file)

    # delete the associated FileInstances, and remove files from disk
    for key in file_instances:
        for fi in file_instances[key]:
            try:
                storage = fi.storage()
                fi.delete()
                storage.delete()
                click.secho(f"{key}\t{fi.uri}", fg="red")

            except Exception as error:
                click.secho(
                    f"cannot delete file '{fi.uri}': {error}", fg="yellow", err=True
                )

    db.session.commit()


@files.group("orphans")
def orphans():
    """Management commands for orphaned files.

    Orphaned files are those that have a FileInstance in the database without any
    associated ObjectVersions.
    """


@orphans.command("list")
@with_appcontext
def list_orphan_files():
    """List orphaned files."""
    for file_instance in get_orphan_files():
        click.echo(file_instance.uri)


@orphans.command("clean")
@click.confirmation_option(
    prompt="Are you sure you want to permanently remove orphan files?"
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Force deletion of files, even if they are marked as not writable",
)
@with_appcontext
def clean_orphan_files(force):
    """Delete orphaned files from DB and storage."""
    for orphan in get_orphan_files():
        file_loc = orphan.uri

        # if the file isn't writable, let's leave it
        if not orphan.writable and not force:
            click.secho(f"{file_loc}: skipped (not writable)", fg="bright_black")
            continue

        try:
            orphan.delete()
            db.session.flush()
            orphan.storage().delete()
            click.secho(file_loc, fg="green")

        except IntegrityError as error:
            click.secho(f"{file_loc}: cannot delete from database: {error}", fg="red")

        except Exception as error:
            click.secho(f"{file_loc}: error: {error}", fg="yellow")

    db.session.commit()


@files.group("zombies")
def zombies():
    """Management commands for unreferenced files.

    Zombie files are those that are still present in the storage, but are not
    referenced by any Location's buckets or FileInstances anymore.
    """


@zombies.command("list")
@with_appcontext
def list_zombie_files():
    """List existing files that aren't referenced in Invenio anymore."""
    for loc in Location.query.all():
        # we only know how to handle directories on the file system for now
        if os.path.isdir(loc.uri):
            click.echo(f"location: {loc.name}")
        else:
            click.secho(
                f"warning: location '{loc.name}' is not a path: {loc.uri}",
                fg="yellow",
            )

        for fp in get_zombie_files(loc):
            click.echo(f"  {fp}")


@zombies.command("clean")
@click.confirmation_option(
    prompt="Are you sure you want to permanently remove zombie files?"
)
@with_appcontext
def clean_zombie_files():
    """Delete existing files that aren't referenced in Invenio anymore."""
    for loc in Location.query.all():
        # we only know how to handle directories on the file system for now
        if not os.path.isdir(loc.uri):
            click.secho(
                f"don't know how to handle location '{loc.name}': skipping",
                fg="yellow",
                err=True,
            )
            continue

        for fp in get_zombie_files(loc):
            try:
                remove_file(fp)
                click.secho(fp, fg="green")

            except PermissionError:
                click.secho(fp, fg="yellow", err=True)
