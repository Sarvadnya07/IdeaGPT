import os
import logging

logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    from celery import Celery
    CELERY_AVAILABLE = True
    celery_app = Celery(
        "ideagpt_worker",
        broker=redis_url,
        backend=redis_url
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
except ImportError:
    CELERY_AVAILABLE = False
    class _DummyConf(dict):
        def update(self, *args, **kwargs):
            super().update(*args, **kwargs)
        def __getattr__(self, name):
            return self.get(name)
        def __setattr__(self, name, value):
            self[name] = value

    class _DummyCelery:
        def __init__(self):
            self.conf = _DummyConf()
        def task(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

    celery_app = _DummyCelery()
    logger.debug("Celery not installed; operating in in-process BackgroundTasks mode.")

