# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2022 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for search indices."""

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records
from invenio_requests.proxies import current_events_service, current_requests_service
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)


@click.group()
def search():
    """Management commands for search indices."""


@search.command("reindex")
@with_appcontext
def reindex_everything():
    """Use all known services to reindex their objects in the search engine.

    (Re-)index all relevant entities for the currently known services.
    Note that this only performs indexing operations, and no indices are cleared
    or torn down and recreated beforehand.

    Current state (regarding known services): App-RDM v9.1.3
    """
    # TODO maybe we could use the 'invenio_records_resources.proxies.service_registry'

    # rebuilding records and drafts
    click.echo("indexing records and drafts... ", nl=False)
    current_rdm_records.records_service.rebuild_index(system_identity)
    click.echo("done.")

    # rebuilding communities and community members
    click.echo("indexing communities and community members... ", nl=False)
    current_communities.service.rebuild_index(system_identity)
    current_communities.service.members.rebuild_index(system_identity)
    click.echo("done.")

    # rebuilding users and groups
    click.echo("indexing users and groups... ", nl=False)
    current_users_service.rebuild_index(system_identity)
    current_groups_service.rebuild_index(system_identity)
    click.echo("done.")

    # rebuilding requests and request events
    click.echo("indexing requests and request events... ", nl=False)
    current_requests_service.rebuild_index(system_identity)
    current_events_service.rebuild_index(system_identity)
    click.echo("done.")

    # rebuilding vocabularies
    click.echo("indexing vocabularies...")
    current_vocabularies = current_app.extensions["invenio-vocabularies"]
    svc_names = (n for n in vars(current_vocabularies) if n.endswith("service"))
    services = ((name, getattr(current_vocabularies, name)) for name in svc_names)
    for name, service in services:
        click.echo(f"> {name}... ", nl=False)
        service.rebuild_index(system_identity)
        click.echo("done.")
