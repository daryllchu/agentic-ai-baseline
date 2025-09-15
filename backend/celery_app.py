from celery import Celery
from kombu import Queue
import os

# Celery configuration
celery_app = Celery(
    "hr_data_hub",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["tasks.etl_tasks"]
)

# Configure task routing
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "tasks.etl_tasks.process_xml_file": {"queue": "etl_queue"},
        "tasks.etl_tasks.validate_xml_file": {"queue": "validation_queue"},
    },
    task_queues=(
        Queue("etl_queue", routing_key="etl"),
        Queue("validation_queue", routing_key="validation"),
    ),
)

if __name__ == "__main__":
    celery_app.start()