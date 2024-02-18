import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_specification(client: AsyncClient) -> None:
    h = {"X-Webauth-User": "user-1"}
    p1 = {
        "short_code": "TLA_PS",
        "name": "project with specifications",
        "groups": ["group_a", "group_b"],
    }

    r = await client.post("/api/projects", headers=h, json=p1)
    assert r.status_code == 200

    p = r.json()

    r = await client.post(
        "/api/specifications",
        headers=h,
        json={
            "project_id": p["id"],
            "name": "spec_1",
            "unit": "test",
            "minimum": 0.0,
            "typical": 1.0,
            "maximum": 2.0,
        },
    )

    assert r.status_code == 201
    sp = r.json()

    url = f"/api/specifications/{sp['id']}"

    # update the name of the test machine
    sp["name"] = "spec_renamed"
    r = await client.put(url, headers=h, json=sp)
    assert r.status_code == 200

    r = await client.get(f"/api/specifications/project/{p['id']}", headers=h)
    assert r.status_code == 200

    sp = r.json()

    assert sp[0]["name"] == "spec_renamed"

    r = await client.delete(url, headers=h)
    assert r.status_code == 200

    # verify it's gone now
    r = await client.get(f"/api/specifications/project/{p['id']}", headers=h)
    assert len(r.json()) == 0
