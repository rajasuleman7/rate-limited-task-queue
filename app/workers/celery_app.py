
from celery import Celery
from ..config import get_settings

def make_celery() -> Celery:
    settings = get_settings()
    celery   = Celery(
        "task_queue",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.workers.tasks"],
    )
    celery.conf.update(
        task_serializer       = "json",
        result_serializer     = "json",
        accept_content        = ["json"],
        task_track_started    = True,
        task_acks_late        = True,
        worker_prefetch_multiplier = 1,
        task_routes = {
            "app.workers.tasks.process_data": {"queue": "default"},
            "app.workers.tasks.send_report":  {"queue": "reports"},
            "app.workers.tasks.run_analysis": {"queue": "analysis"},
        },
    )
    return celery

celery_app = make_celery()
