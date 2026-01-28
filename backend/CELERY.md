# Celery Worker Configuration

This document explains how to run and configure the Celery worker for background task processing.

## Running the Worker

### Development Mode

**Single worker (all queues):**
```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

**With autoreload (development):**
```bash
watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- celery -A celery_worker.celery_app worker --loglevel=info
```

### Production Mode

**Multiple workers with queue routing:**
```bash
# Evaluation queue (CPU-intensive)
celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=4 --queue=evaluation --hostname=evaluation@%h

# Rewrite queue (LLM calls)
celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=2 --queue=rewrite --hostname=rewrite@%h

# Escalation queue (low priority)
celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=2 --queue=escalation --hostname=escalation@%h

# Default queue
celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=4 --queue=celery --hostname=default@%h
```

## Task Queues

Tasks are routed to specific queues based on their type:

- **evaluation**: AI detector and AEO scoring tasks
- **rewrite**: LLM-based rewrite generation tasks
- **escalation**: Human escalation and notification tasks
- **celery** (default): All other tasks

## Monitoring

### Flower (Web UI)

```bash
pip install flower
celery -A celery_worker.celery_app flower
```

Access at: http://localhost:5555

### Command Line

**List active tasks:**
```bash
celery -A celery_worker.celery_app inspect active
```

**List registered tasks:**
```bash
celery -A celery_worker.celery_app inspect registered
```

**Worker stats:**
```bash
celery -A celery_worker.celery_app inspect stats
```

**Purge all tasks:**
```bash
celery -A celery_worker.celery_app purge
```

## Task Configuration

### Base Task Classes

- **`BaseTask`**: Default task with automatic retry (max 3 retries)
- **`IdempotentTask`**: Safe to retry aggressively (max 5 retries)
- **`CriticalTask`**: No automatic retry (e.g., LLM calls)

### Retry Behavior

Tasks automatically retry with exponential backoff:
- Initial delay: 60 seconds
- Backoff multiplier: 2x
- Max delay: 10 minutes
- Jitter: Random delay added to prevent thundering herd

### Time Limits

- **Soft limit**: 4.5 minutes (raises `SoftTimeLimitExceeded`)
- **Hard limit**: 5 minutes (kills task)

## Health Check

Test Celery connectivity:
```bash
celery -A celery_worker.celery_app call tasks.health_check
```

## Troubleshooting

### Worker not picking up tasks

1. Check Redis connection:
   ```bash
   redis-cli ping
   ```

2. Verify worker is running:
   ```bash
   celery -A celery_worker.celery_app inspect active_queues
   ```

3. Check task routing:
   ```bash
   celery -A celery_worker.celery_app inspect registered
   ```

### Tasks stuck in "pending"

1. Check worker logs for errors
2. Verify task serialization (must be JSON-compatible)
3. Check time limits (task may be timing out)

### Memory leaks

Workers restart after 1000 tasks to prevent memory leaks:
```python
worker_max_tasks_per_child=1000
```

## Production Deployment

Use a process manager like systemd or supervisord:

**systemd example (`/etc/systemd/system/celery-worker.service`):**
```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/app/backend
ExecStart=/usr/local/bin/celery -A celery_worker.celery_app worker --loglevel=warning --concurrency=4 --pidfile=/var/run/celery/%n.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
```
