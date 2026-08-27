"""
IdeaGPT AI Gateway — Workload Bulkheads.
Separates concurrent execution capacity across:
  - Interactive requests (e.g. Chat / Live Tools)
  - Background AI tasks (e.g. Asynchronous Evaluation Tasks)
  - Web research jobs
  - Embedding / Similarity computations
"""

import asyncio
from typing import Dict

class WorkloadBulkhead:
    # Concurrency limit semaphores
    _semaphores: Dict[str, asyncio.Semaphore] = {
        "interactive": asyncio.Semaphore(20),
        "background": asyncio.Semaphore(10),
        "research": asyncio.Semaphore(5),
        "embedding": asyncio.Semaphore(15),
    }

    @classmethod
    def get_semaphore(cls, workload_type: str) -> asyncio.Semaphore:
        return cls._semaphores.get(workload_type, cls._semaphores["interactive"])
