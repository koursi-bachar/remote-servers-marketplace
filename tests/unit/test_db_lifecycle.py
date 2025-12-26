import pytest
from app.database import get_db


def test_get_db_generator_closes():
    """
    This ensures the get_db() dependency correctly makes a session,
    and then closes it when the DB is exhausted.
    """
    gen = get_db()
    db = next(gen)
    assert db is not None

    with pytest.raises(StopIteration):
        next(gen)