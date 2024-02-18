# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Commands for generating reports."""

import click
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_rdm_records.proxies import current_rdm_records_service as rdm_service

from .utils import bytes_to_human, is_owned_by


@click.group()
def reports():
    """Commands for generating reports."""


@reports.command("uploads-per-year")
@with_appcontext
def uploads_per_year():
    """Report the published uploads per year."""
    sep = "\t"
    rec_cls = rdm_service.record_cls
    records = [rec_cls(rm.data, model=rm) for rm in rec_cls.model_cls.query.all()]
    years = sorted({rec.created.year for rec in records})
    years_records_files = {
        year: {
            rec["id"]: {fn: e.file.size for fn, e in rec.files.entries.items()}
            for rec in records
            if rec.created.year == year
        }
        for year in years
    }

    for year in years_records_files:
        records_files = years_records_files[year]
        num_recs = len(records_files)
        num_files = sum([len(files) for files in records_files.values()])
        upload_sizes = sum(
            [sum(s for s in files.values()) for files in records_files.values()]
        )

        click.echo(
            f"{year}{sep}{num_recs} records{sep}{num_files} files{sep}{bytes_to_human(upload_sizes)}"
        )


@reports.command("uploads-per-user")
@with_appcontext
def uploads_per_user():
    """Generate a list of uploads per user."""
    users = User.query.all()
    rec_cls = rdm_service.record_cls
    records = [rec_cls(rm.data, model=rm) for rm in rec_cls.model_cls.query.all()]

    records_per_user = {
        u: [rec for rec in records if is_owned_by(u, rec)] for u in users
    }

    # sort the users according to the number of their uploads
    for user, records in sorted(records_per_user.items(), key=lambda e: len(e[1])):
        if not records:
            continue

        click.echo(f"{user.id} {user.email}: {len(records)} records")
        for rec in records:
            click.echo(f"  {rec.pid.pid_value}")
        click.echo()
