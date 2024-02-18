import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_testrun(client: AsyncClient) -> None:
    h = {"X-Webauth-User": "user-1"}
    p1 = {
        "short_code": "TLA_P1",
        "name": "project with groups",
        "groups": ["group_a", "group_b"],
    }

    r = await client.post("/api/projects", headers=h, json=p1)
    assert r.status_code == 200

    p = r.json()

    r = await client.post(
        "/api/testruns",
        headers=h,
        json={
            "project_id": p["id"],
            "dut_id": "device_1",
            "machine_hostname": "test",
            "user_name": "user-1",
            "test_name": "unit-test",
            "data": {"a": "b"},
        },
    )

    assert r.status_code == 201
    tr = r.json()

    url = f"/api/testruns/{tr['id']}"

    # update the name of the test machine
    tr["machine_hostname"] = "other-machine"
    r = await client.put(url, headers=h, json=tr)
    assert r.status_code == 200

    r = await client.get(url, headers=h)
    assert r.status_code == 200

    tr = r.json()

    assert tr["machine_hostname"] == "other-machine"

    # set up the testrun
    r = await client.post(
        f"/api/testruns/setup/{tr['id']}", headers=h, json={"steps": [], "columns": {}}
    )
    assert r.status_code == 200

    # start the testrun
    r = await client.put(f"/api/testruns/start/{tr['id']}", headers=h)
    assert r.status_code == 200

    # mark it as failed
    r = await client.put(f"/api/testruns/fail/{tr['id']}", headers=h)
    assert r.status_code == 200

    # set a field
    r = await client.put(
        f"/api/testruns/{tr['id']}/field/quality", headers=h, json="garbage"
    )
    assert r.status_code == 200
    data = r.json()
    assert data["data"]["quality"] == "garbage"

    # before we delete it
    r = await client.delete(url, headers=h)
    assert r.status_code == 200

    # verify it's gone now
    r = await client.get(url, headers=h)
    assert r.status_code == 404
