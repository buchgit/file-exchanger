import sys
from pathlib import Path

# Make server/ importable without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import create_access_token, hash_password, init_admin
from config import settings
from database import Base, get_db
from main import app
from models import User


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    init_admin(session)
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_app(db_session, tmp_storage):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
def tmp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_PATH", tmp_path)
    return tmp_path


@pytest.fixture(scope="function")
def admin_token(db_session):
    admin = db_session.query(User).filter(User.is_admin == True).first()
    return create_access_token({"sub": str(admin.id)})


@pytest.fixture(scope="function")
def regular_user(db_session):
    user = User(
        username="testuser",
        password_hash=hash_password("testpass"),
        is_admin=False,
        force_change_password=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def user_token(regular_user):
    return create_access_token({"sub": str(regular_user.id)})
