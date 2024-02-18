..
    Copyright (C) 2020 - 2021 TU Wien.

    Invenio-Utilities-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 2024.1 (released 2024-02-08)

- Add CLI commands for generating simple reports about the number of records


Version 2022.2 (released 2022-07-19, updated 2022-11-23)

- v9 compat: Replace usage of user.profile with user.user_profile
- Add CLI command for showing users' API tokens
- Add CLI command for calling all known services' ``rebuild_index()``
- Migrate from setup.py to setup.cfg


Version 2022.1 (released 2022-03-25, updated 2022-07-04)

- Rename old 'orphans' subcommand for files to 'zombies'
- Add 'orphans' subcommand for files that operates on orphaned DB entries
- Add command to verify the integrity of all files
- Update file verification commands for drafts and records
- Automatically increase bucket limits when adding files to drafts


Version 2021.2 (released 2021-12-07, updated 2021-12-15)

- Bump dependencies (InvenioRDM v7)
- Add option to show/hide users' full names


Version 2021.1 (released 2021-07-15)

- Initial public release.
