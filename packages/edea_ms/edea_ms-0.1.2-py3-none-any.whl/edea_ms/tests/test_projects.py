import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_projects_with_groups(client: AsyncClient) -> None:
    p1 = {
        "short_code": "TLA_P1",
        "name": "project with groups",
        "groups": ["group_a", "group_b"],
    }
    p2 = {
        "short_code": "TLA_P2",
        "name": "project with groups",
        "groups": ["group_c", "group_d"],
    }
    p3 = {
        "short_code": "TLA_P3",
        "name": "project with groups",
        "groups": ["group_a", "group_d"],
    }
    p4 = {
        "short_code": "TLA_P4",
        "name": "project with groups",
        "groups": ["group_x", "group_y"],
    }

    r = await client.post("/api/projects", json=p1)
    assert r.status_code == 200
    r = await client.post("/api/projects", json=p2, headers={"X-Webauth-User": "user-2"})
    assert r.status_code == 200
    r = await client.post("/api/projects", json=p3, headers={"X-Webauth-User": "user-3"})
    assert r.status_code == 200
    r = await client.post("/api/projects", json=p4, headers={"X-Webauth-User": "user-4"})
    assert r.status_code == 200


@pytest.mark.anyio
async def test_list_projects(client: AsyncClient) -> None:
    # user-5 should have access to TLA_P1 and TLA_P2 because because of common group membership
    r = await client.get(
        "/api/projects", headers={"X-Webauth-User": "user-5", "X-Webauth-Groups": "group_a"}
    )

    v = r.json()
    assert len(v) == 2
    assert v[0]["short_code"] == "TLA_P1"
    assert v[1]["short_code"] == "TLA_P3"


@pytest.mark.anyio
async def test_no_projects_visible_for_group(client: AsyncClient) -> None:
    # change the group membership of user-4 and see that there's no more projects visible
    r = await client.get(
        "/api/projects", headers={"X-Webauth-User": "user-5", "X-Webauth-Groups": "group_e"}
    )

    v = r.json()
    assert len(v) == 0


@pytest.mark.anyio
async def test_creator_but_wrong_groups_visible(client: AsyncClient) -> None:
    # user-4 has the wrong group membership, but should still see the project they created
    # this is for the case when you have a dedicated user which sets up projects, but is not
    # a member of the groups that the projects get set up for.
    r = await client.get(
        "/api/projects", headers={"X-Webauth-User": "user-4", "X-Webauth-Groups": "group_e"}
    )

    v = r.json()
    assert len(v) == 1
    assert v[0]["short_code"] == "TLA_P4"


@pytest.mark.anyio
async def test_update_project(client: AsyncClient) -> None:
    r = await client.get("/api/projects/TLA_P2", headers={"X-Webauth-User": "user-2"})

    v = r.json()

    v["name"] = "naming things is a hard problem"

    r = await client.put(
        "/api/projects/TLA_P2", json=v, headers={"X-Webauth-User": "user-2"}
    )
    assert r.status_code == 200
    d = r.json()

    assert v["name"] == d["name"]


@pytest.mark.anyio
async def test_delete_project(client: AsyncClient) -> None:
    r = await client.delete("/api/projects/TLA_P2", headers={"X-Webauth-User": "user-2"})
    assert r.status_code == 200

    r = await client.get("/api/projects/TLA_P2", headers={"X-Webauth-User": "user-2"})
    assert r.status_code == 404


@pytest.mark.anyio
async def test_delete_project_wrong_group(client: AsyncClient) -> None:
    r = await client.delete("/api/projects/TLA_P4", headers={"X-Webauth-User": "user-2"})
    assert r.status_code == 404
