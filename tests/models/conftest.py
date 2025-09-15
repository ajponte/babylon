import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.models import BASE


@pytest.fixture(scope="function")
def db_session():
    # Setup
    engine = create_engine("sqlite:///:memory:")
    BASE.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Teardown
    session.close()
    BASE.metadata.drop_all(engine)
