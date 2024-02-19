import json

from .cli import (
    create_tables,
    list_bovine_names_from_db,
    register_new_user,
    handle_actor_profile,
)


async def test_cli_methods(tmp_path):
    db_url = f"sqlite://{tmp_path}/db.sqlite"
    await create_tables(db_url=db_url)

    names = await list_bovine_names_from_db(db_url)

    assert names == []

    bovine_name = await register_new_user(db_url, "domain.example", "user")

    names = await list_bovine_names_from_db(db_url)

    assert names == [bovine_name]


async def test_cli_profile(tmp_path):
    db_url = f"sqlite://{tmp_path}/db.sqlite"
    await create_tables(db_url=db_url)

    bovine_name = await register_new_user(db_url, "domain.example", "user")

    filename = f"{tmp_path}/profile.json"

    with open(filename, "w") as fp:
        json.dump({"summary": "a summary"}, fp)

    profile = await handle_actor_profile(db_url, bovine_name, filename=filename)

    assert profile["summary"] == "a summary"


async def test_cli_profile_summary_map(tmp_path):
    db_url = f"sqlite://{tmp_path}/db.sqlite"
    await create_tables(db_url=db_url)

    bovine_name = await register_new_user(db_url, "domain.example", "user")

    filename = f"{tmp_path}/profile.json"

    summary_map = {"en": "summary", "de": "Beschreibung"}

    with open(filename, "w") as fp:
        json.dump({"summaryMap": summary_map}, fp)

    profile = await handle_actor_profile(db_url, bovine_name, filename=filename)

    assert "summary" not in profile
    assert profile["summaryMap"] == summary_map
