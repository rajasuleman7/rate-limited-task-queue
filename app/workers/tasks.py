
"""
Celery task definitions.
Each task simulates a realistic background job with progress tracking.
"""
import time
import random
import logging

logger = logging.getLogger("celery.tasks")

try:
    from .celery_app import celery_app
    CELERY_AVAILABLE = True
except Exception:
    CELERY_AVAILABLE = False


def _simulate_task(name: str, duration: float, fail_rate: float = 0.05) -> dict:
    """Simulate a task with realistic processing time and occasional failures."""
    if random.random() < fail_rate:
        raise RuntimeError(f"Task {name} failed (simulated)")
    time.sleep(duration)
    return {"task": name, "status": "completed", "duration_s": duration}


if CELERY_AVAILABLE:
    @celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
    def process_data(self, payload: dict) -> dict:
        """Process a data payload — simulates ETL or transformation work."""
        try:
            logger.info("process_data task_id=%s", self.request.id)
            result = _simulate_task("process_data", duration=random.uniform(0.5, 2.0))
            result["input_keys"] = list(payload.keys())
            return result
        except RuntimeError as e:
            raise self.retry(exc=e)

    @celery_app.task(bind=True, max_retries=2)
    def send_report(self, report_type: str, recipient: str) -> dict:
        """Generate and send a report."""
        try:
            result = _simulate_task("send_report", duration=random.uniform(0.3, 1.0))
            result["report_type"] = report_type
            result["recipient"]   = recipient
            return result
        except RuntimeError as e:
            raise self.retry(exc=e)

    @celery_app.task(bind=True, time_limit=60)
    def run_analysis(self, dataset_id: str, config: dict) -> dict:
        """Run heavy analysis — assigned to the analysis queue."""
        result = _simulate_task("run_analysis", duration=random.uniform(1.0, 3.0))
        result["dataset_id"] = dataset_id
        return result
else:
    # Stub implementations when Celery/Redis unavailable (for testing)
    class _StubTask:
        def delay(self, *args, **kwargs):
            return _StubResult()
        def apply_async(self, *args, **kwargs):
            return _StubResult()

    class _StubResult:
        id = "stub-task-id"
        def __init__(self): self.id = "stub-task-id"

    process_data = _StubTask()
    send_report  = _StubTask()
    run_analysis = _StubTask()
