import csv, io, os
from datetime import datetime
from typing import List, Dict, Any

from redis import Redis
from rq import Queue

from .db import db
from .models import Lead, IdempotencyKey

# One queue, shared by web/worker via REDIS_URL
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(redis_url)
queue = Queue(connection=redis_conn)

CHUNK_SIZE = 500

def enqueue_bulk_import(csv_content: str, idempotency_key: str | None) -> str:
    """Enqueue bulk CSV import. Returns RQ job id."""
    job = queue.enqueue(process_bulk_import, csv_content, idempotency_key, timeout="30m")
    return job.id

def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "full_name": (row.get("full_name") or "").strip() or None,
        "email": (row.get("email") or "").strip().lower() or None,
        "phone": (row.get("phone") or "").strip() or None,
        "source": (row.get("source") or "bulk").strip() or "bulk",
        "status": (row.get("status") or "new").strip() or "new",
        "business_id": 1,
    }

def process_bulk_import(csv_content: str, idempotency_key: str | None) -> Dict[str, Any]:
    """Process a CSV import in the background (chunks, upserts)."""
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)

    created = 0
    updated = 0
    errors: List[str] = []

    for i in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[i : i + CHUNK_SIZE]
        for j, row in enumerate(chunk):
            idx = i + j + 1
            try:
                data = _normalize_row(row)
                if not any([data["full_name"], data["email"], data["phone"]]):
                    continue

                existing = None
                if data["email"]:
                    existing = Lead.query.filter_by(email=data["email"]).first()
                if not existing and data["phone"]:
                    existing = Lead.query.filter_by(phone=data["phone"]).first()

                if existing:
                    for k, v in data.items():
                        if v is not None:
                            setattr(existing, k, v)
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    db.session.add(Lead(**data))
                    created += 1
            except Exception as e:
                errors.append(f"Row {idx}: {e}")

        db.session.commit()

    result = {"created": created, "updated": updated, "errors": errors, "total_rows": len(rows)}

    if idempotency_key:
        rec = IdempotencyKey.query.filter_by(key=idempotency_key).first()
        if rec:
            rec.response_data = result
            db.session.commit()

    return result
