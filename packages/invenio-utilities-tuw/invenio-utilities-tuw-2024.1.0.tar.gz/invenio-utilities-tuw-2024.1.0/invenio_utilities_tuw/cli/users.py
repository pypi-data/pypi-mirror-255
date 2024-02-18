# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for users."""

import click
from flask.cli import with_appcontext
from invenio_accounts.models import User

from ..utils import get_user_by_identifier, similarity
from .options import (
    option_hide_user_names,
    option_hide_user_roles,
    option_only_list_active_users,
)


@click.group()
def users():
    """Management commands for users."""


@users.command("list")
@option_only_list_active_users
@option_hide_user_names
@option_hide_user_roles
@with_appcontext
def list_users(only_active, show_names, show_roles):
    """List registered users."""
    users = User.query.order_by(User.id)

    if only_active:
        users = users.filter_by(active=True)

    for user in users:
        line = f"{user.id} {user.email}"
        if show_names:
            name = "N/A"
            if full_name := user.user_profile.get("full_name"):
                name = f"({full_name})"
            line += f" {name}"

        if show_roles:
            line += f" {[r.name for r in user.roles]}"

        fg = "green" if user.active else "red"
        click.secho(line, fg=fg)


@users.command("show")
@option_hide_user_names
@option_hide_user_roles
@click.argument("user_id")
@with_appcontext
def show_user(user_id, show_names, show_roles):
    """Show more information about the specified user."""
    user = get_user_by_identifier(user_id)
    name = "N/A"
    if full_name := user.user_profile.get("full_name"):
        name = f"({full_name})"

    line = f"{user.id} {user.email}"
    if show_names:
        line += f" {name}"

    if show_roles:
        line += f" {[r.name for r in user.roles]}"

    fg = "green" if user.active else "red"
    click.secho(line, fg=fg)


@users.command("find")
@option_only_list_active_users
@click.option(
    "--full-name",
    "-n",
    "full_name",
    is_flag=True,
    default=False,
    help="query the user's full name instead of the email address",
)
@click.argument("query")
@with_appcontext
def find_user(only_active, query, full_name):
    """Find users with the given (or similar) email address."""
    users = User.query.order_by(User.id)

    if only_active:
        users = users.filter_by(active=True)

    all_users = users.all()
    if all_users:

        def query_similarity(user):
            if full_name:
                value = user.user_profile.get("full_name", "")
            else:
                value = user.email

            return similarity(value, query)

        # find the best match among all users
        match = max(all_users, default=None, key=query_similarity)

        if match:
            fg = "green" if match.active else "red"
            line = f"{match.id} {match.email}"
            click.secho(line, fg=fg)
        else:
            click.secho("no match found.", fg="yellow")

    else:
        click.secho("no users registered.", fg="yellow")


@users.command("tokens")
@click.argument("user_id")
@with_appcontext
def show_user_tokens(user_id):
    """Show the user's API tokens."""
    user = get_user_by_identifier(user_id)
    for token in user.oauth2tokens:
        fg = "bright_black" if token.is_internal else "white"
        # TODO optionally show scopes for the tokens

        name = "N/A"
        if token.client and token.client.name:
            name = token.client.name

        click.secho(f'{token.access_token}  "{name}"', fg=fg)
