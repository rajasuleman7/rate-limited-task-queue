
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth         import get_current_user
from ..rate_limiter import rate_limit, check_rate_limit
from ..workers.tasks import process_data, send_report, run_analysis

router = APIRouter()
logger = logging.getLogger("tasks.router")

# In-memory job store
_jobs: dict[str, dict] = {}


class JobSubmit(BaseModel):
    task_type: str   # process_data | send_report | run_analysis
    payload:   dict = {}


class JobResponse(BaseModel):
    job_id:     str
    task_type:  str
    status:     str
    submitted_at: str
    submitted_by: str


@router.post("/submit", response_model=JobResponse,
             dependencies=[Depends(rate_limit())])
def submit_job(body: JobSubmit, user: dict = Depends(get_current_user)):
    task_map = {
        "process_data": process_data,
        "send_report":  send_report,
        "run_analysis": run_analysis,
    }
    if body.task_type not in task_map:
        raise HTTPException(400, f"Unknown task type. Choose from: {list(task_map)}")

    job_id = str(uuid.uuid4())
    task   = task_map[body.task_type]

    try:
        if body.task_type == "process_data":
            result = task.delay(body.payload)
        elif body.task_type == "send_report":
            result = task.delay(
                body.payload.get("report_type", "summary"),
                body.payload.get("recipient", user["username"]),
            )
        else:
            result = task.delay(
                body.payload.get("dataset_id", "default"),
                body.payload.get("config", {}),
            )
        celery_id = getattr(result, "id", job_id)
    except Exception as e:
        logger.error("Task dispatch failed: %s", e)
        celery_id = job_id

    now  = datetime.now(timezone.utc).isoformat()
    _jobs[job_id] = {
        "job_id":       job_id,
        "celery_id":    celery_id,
        "task_type":    body.task_type,
        "status":       "queued",
        "submitted_at": now,
        "submitted_by": user["username"],
        "user_id":      user["sub"],
    }
    logger.info("job_submitted job_id=%s task=%s user=%s",
                job_id, body.task_type, user["username"])
    return JobResponse(
        job_id=job_id, task_type=body.task_type,
        status="queued", submitted_at=now,
        submitted_by=user["username"],
    )


@router.get("/{job_id}")
def get_job(job_id: str, user: dict = Depends(get_current_user)):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    # Users can only see their own jobs unless admin
    if job["user_id"] != user["sub"] and user.get("role") != "admin":
        raise HTTPException(403, "Access denied")
    return job


@router.get("")
def list_jobs(user: dict = Depends(get_current_user)):
    if user.get("role") == "admin":
        return list(_jobs.values())
    return [j for j in _jobs.values() if j["user_id"] == user["sub"]]


@router.get("/rate-limit/status")
def rate_limit_status(user: dict = Depends(get_current_user)):
    status = check_rate_limit(user["sub"], user.get("role", "user"))
    return {**status, "username": user["username"], "role": user.get("role")}
