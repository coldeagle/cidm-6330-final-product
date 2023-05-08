import pytest
import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_202_and_enrollment_is_created():
    # Need to create test data for activity and enrollment period
    r = api_client.enrollment_add(enrollment_period_id=1, student_id=1, balance=100, price=100)

    assert r.status_code == 202

    r = api_client.enrollment_get(r.json()['Id'])
    assert r.ok
    assert r.json()['enrollment_period_id'] == 1


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    r = api_client.enrollment_add(enrollment_period_id=None, student_id=1, balance=100, price=100)
    assert r.status_code == 400
