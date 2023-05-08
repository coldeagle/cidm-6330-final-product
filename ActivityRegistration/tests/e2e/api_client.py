import requests
from enrollment_handling import config
from enrollment_handling.domain import models


def enrollment_add(student_id, enrollment_period_id, balance, price):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/enroll/add", json={"StudentId": student_id, "EnrollmentPeriodId": enrollment_period_id, "Balance": balance, "Price": price}
    )
    assert r.status_code == 201


def enrollment_edit(id, student_id, enrollment_period_id, balance, price):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/enroll/{id}/edit", json={"StudentId": student_id, "EnrollmentPeriodId": enrollment_period_id, "Balance": balance, "Price": price}
    )
    assert r.status_code == 201


def enrollment_get(id):
    url = config.get_api_url()
    return requests.get(
        f'{url}/enroll/{id}'
    )
