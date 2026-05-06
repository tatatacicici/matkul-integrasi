import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.models import User
from app.core.security import hash_password
from app.core.jwt import create_access_token

from sqlalchemy.pool import StaticPool

# Gunakan SQLite in-memory untuk testing agar cepat dan terisolasi
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Setup testing DB and provide a session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Provide a TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    # Patch main.engine so lifespan doesn't hit real DB
    import app.main as main_module
    main_module.engine = engine
    
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Buat dummy user pertama."""
    user = User(
        name="Test User",
        email="test@user.com",
        password=hash_password("qwerty")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authorized_client(client, test_user):
    """TestClient yang sudah di-inject dengan JWT Token milik test_user."""
    token = create_access_token(test_user.id, test_user.email)
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture(scope="function")
def other_user(db_session):
    """Buat dummy user kedua untuk skenario ownership."""
    user = User(
        name="Other User",
        email="other@user.com",
        password=hash_password("qwerty")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def other_authorized_client(client, other_user):
    """TestClient yang sudah di-inject dengan JWT Token milik other_user."""
    token = create_access_token(other_user.id, other_user.email)
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
