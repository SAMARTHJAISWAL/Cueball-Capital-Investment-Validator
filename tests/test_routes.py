import pytest

from app import create_app, init_db
from config.config import Config


@pytest.fixture
def client(tmp_path):
    class TestConfig(Config):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'test.db'}"
        TESTING = True

    app = create_app(TestConfig)
    init_db(app)
    return app.test_client()


def ids(response):
    return [item["id"] for item in response.get_json()]


def test_home(client):
    assert client.get("/").get_json()["status"] == "API is running"


def test_budget_rules_loaded(client):
    rules = client.get("/api/budget_rules").get_json()
    assert len(rules) == 5
    assert rules[1] == {"id": 2, "amount": 30.0, "time_period": None, "sector": "FinTech"}


def test_investments(client):
    assert ids(client.get("/api/investments")) == list(range(1, 11))
    sorted_dates = [i["date"] for i in client.get("/api/investments?sort=true").get_json()]
    assert sorted_dates[0] == "06/01/2020" and sorted_dates[-1] == "18/05/2020"


def test_valid_and_violating_partition_the_sample_data(client):
    # Feb 2020 exceeds the 75/month cap from investment 4 on; FinTech's all-time
    # cap of 30 is exceeded by investment 3; BigData's Q1 cap of 25 by 8; May by 10.
    assert ids(client.get("/api/valid_investments")) == [1, 2, 9]
    assert ids(client.get("/api/violating_investments")) == [3, 4, 5, 6, 7, 8, 10]


def test_init_db_is_idempotent(client, tmp_path):
    class TestConfig(Config):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'test.db'}"

    app = create_app(TestConfig)
    init_db(app)  # second call must not re-insert rows
    assert len(app.test_client().get("/api/investments").get_json()) == 10
