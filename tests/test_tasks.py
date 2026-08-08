
def test_submit_job_requires_auth(client):
    r = client.post("/tasks/submit", json={"task_type":"process_data"})
    assert r.status_code in (401, 403)

def test_submit_process_data(client, auth_headers):
    r = client.post("/tasks/submit",
                    json={"task_type":"process_data","payload":{"key":"val"}},
                    headers=auth_headers)
    assert r.status_code == 200
    d = r.json()
    assert "job_id"   in d
    assert d["status"] == "queued"

def test_submit_unknown_task(client, auth_headers):
    r = client.post("/tasks/submit",
                    json={"task_type":"invalid_task"},
                    headers=auth_headers)
    assert r.status_code == 400

def test_get_own_job(client, auth_headers):
    r    = client.post("/tasks/submit",
                       json={"task_type":"process_data"},
                       headers=auth_headers)
    jid  = r.json()["job_id"]
    r2   = client.get(f"/tasks/{jid}", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["job_id"] == jid

def test_cannot_get_other_users_job(client, auth_headers, admin_headers):
    r   = client.post("/tasks/submit",
                      json={"task_type":"process_data"},
                      headers=admin_headers)
    jid = r.json()["job_id"]
    r2  = client.get(f"/tasks/{jid}", headers=auth_headers)
    assert r2.status_code == 403

def test_list_own_jobs(client, auth_headers):
    client.post("/tasks/submit", json={"task_type":"process_data"}, headers=auth_headers)
    client.post("/tasks/submit", json={"task_type":"send_report"},  headers=auth_headers)
    r = client.get("/tasks", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 2

def test_rate_limit_status(client, auth_headers):
    r = client.get("/tasks/rate-limit/status", headers=auth_headers)
    assert r.status_code == 200
    assert "remaining" in r.json()
    assert "limit"     in r.json()
