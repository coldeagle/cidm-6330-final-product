import json
import pytest
from datetime import date, datetime, timedelta
from tenacity import Retrying, RetryError, stop_after_delay
import api_client
import redis_client



@pytest.mark.usefixtures("in_memory_sqlite_db")
@pytest.mark.usefixtures("restart_api")
@pytest.mark.usefixtures("restart_redis_pubsub")
def test_change_batch_quantity_leading_to_reallocation():
    redis_client.publish_message('activity_added_published', dict(ActivityId=1, Active=True, Description='Soccer club', LeadByEmployeeId=1, Name='Soccer', Type='sport'))
    redis_client.publish_message('activity_updated_published', dict(ActivityId=1, Active=True, Description='Soccer club', LeadByEmployeeId=2, Name='Soccer', Type='sport'))
    redis_client.publish_message('activity_deleted_published', dict(ActivityId=1))

    redis_client.publish_message('enrollment_period_added_published', dict(EnrollmentPeriodId=1, ActivityId=1, Capacity=100, NumEnrolled=0, ListPrice=100.00,StartDate=date.today(), EndDate=date.today()+timedelta(days=30)))
    redis_client.publish_message('enrollment_period_updated_published', dict(EnrollmentPeriodId=1, ActivityId=1, Capacity=100, NumEnrolled=50, ListPrice=100.00,StartDate=date.today(), EndDate=date.today()+timedelta(days=30)))
    redis_client.publish_message('enrollment_period_deleted_published', dict(EnrollmentPeriodId=1))

    # would test to make sure that the items got added when publisehd; however, I was unable to get redis running in test even in the allocation app

