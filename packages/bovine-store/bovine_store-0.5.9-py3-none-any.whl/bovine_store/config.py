# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT


def tortoise_config(db_url: str) -> dict:
    return {
        "connections": {"default": db_url},
        "apps": {
            "models": {
                "models": [
                    "bovine_store.models",
                ],
                "default_connection": "default",
            },
        },
    }
