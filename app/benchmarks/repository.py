from typing import List, Optional
from sqlalchemy.orm import Session
from .models import MachineBenchmark
from .schemas import BenchmarkCreate


class BenchmarksRepository:
    """Repository for managing machine benchmark data in the database."""
    def create(self, db: Session, machine_id, payload: BenchmarkCreate) -> MachineBenchmark:
        obj = MachineBenchmark(
            machine_id=machine_id,
            listing_id=payload.listing_id,
            name=payload.name,
            score=payload.score,
            methodology_uri=str(payload.methodology_uri) if payload.methodology_uri else None,
            artifact_uri=str(payload.artifact_uri) if payload.artifact_uri else None,
        )

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def list_for_machine(self, db: Session, machine_id) -> List[MachineBenchmark]:
        return (
            db.query(MachineBenchmark)
            .filter(MachineBenchmark.machine_id == machine_id)
            .order_by(MachineBenchmark.created_at.desc())
            .all()
        )

    def list_for_listing(self, db: Session, listing_id) -> List[MachineBenchmark]:
        return (
            db.query(MachineBenchmark)
            .filter(MachineBenchmark.listing_id == listing_id)
            .order_by(MachineBenchmark.created_at.desc())
            .all()
        )