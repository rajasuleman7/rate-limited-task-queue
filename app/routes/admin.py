
from fastapi import APIRouter, Depends
from ..auth import require_role
from .tasks import _jobs

router = APIRouter()


@router.get("/jobs", dependencies=[Depends(require_role("admin"))])
def all_jobs():
    return {"total": len(_jobs), "jobs": list(_jobs.values())}


@router.get("/stats", dependencies=[Depends(require_role("admin"))])
def stats():
    from ..auth import _users
    statuses = {}
    for j in _jobs.values():
        statuses[j["status"]] = statuses.get(j["status"], 0) + 1
    return {
        "total_users": len(_users),
        "total_jobs":  len(_jobs),
        "by_status":   statuses,
    }
