
def test_admin_can_see_all_jobs(client, auth_headers, admin_headers):
    client.post("/tasks/submit", json={"task_type":"process_data"}, headers=auth_headers)
    r = client.get("/admin/jobs", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total"] >= 1

def test_user_cannot_access_admin(client, auth_headers):
    r = client.get("/admin/jobs", headers=auth_headers)
    assert r.status_code == 403

def test_admin_stats(client, admin_headers, auth_headers):
    client.post("/tasks/submit", json={"task_type":"process_data"}, headers=auth_headers)
    r = client.get("/admin/stats", headers=admin_headers)
    assert r.status_code == 200
    assert "total_jobs" in r.json()
