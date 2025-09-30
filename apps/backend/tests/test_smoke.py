
"""Basic integration smoke tests for Chess Coach backend."""

import importlib
import uuid


def test_guid_primary_keys_work_with_sqlite(tmp_path, monkeypatch):
    """Ensure tables create and GUID primary keys behave on SQLite."""
    db_file = tmp_path / 'smoke.sqlite'
    monkeypatch.setenv('POSTGRES_URL', f'sqlite:///{db_file}')

    # Reload modules so they pick up the new database URL.
    app_models = importlib.import_module('app.models')
    importlib.reload(app_models)
    app_db = importlib.import_module('app.db')
    importlib.reload(app_db)

    # Create schema and persist a simple game.
    app_db.create_tables()
    session = app_db.SessionLocal()
    try:
        game = app_models.Game(
            username='smoke-user',
            pgn="""[Event "Smoke Test"]
[Site "Lichess"]
[Date "2024.01.01"]
[Round "-"]
[White "White"]
[Black "Black"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0""",
        )
        session.add(game)
        session.commit()

        stored = session.query(app_models.Game).one()
        assert isinstance(stored.id, uuid.UUID)
        assert stored.username == 'smoke-user'
    finally:
        session.close()
