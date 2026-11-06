# Workers & Supervisor

Durable job state will live in PostgreSQL. Redis/Celery will schedule isolated worker tasks.

No worker or browser should run as root. One browser task at a time is the initial safety target until benchmarking provides a measured limit.

Implementation begins in Stages 21–25.
