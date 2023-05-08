# pylint: disable=no-self-use
from __future__ import annotations
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List
import pytest
from enrollment_handling import bootstrap
from enrollment_handling.domain import commands
from enrollment_handling.service_layer import handlers
from enrollment_handling.adapters import notifications, repository
from enrollment_handling.service_layer import unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, enrollments):
        super().__init__()
        self.enrollments = set(enrollments)

    def _add(self, enrollment):
        self.enrollments.add(enrollment)

    def _get(self, id):
        return next((e for e in self.enrollments if e.Id == id), None)

    def _get_by_student_and_enrollment_period(self, student_id: int, enrollment_period_id: int):
        return next((e for e in self.enrollments if e.StudentId == student_id and e.EnrollmentPeriodId == enrollment_period_id), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.enrollments = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
    )


class TestEnrollment:
    def test_add_and_update(self):
        bus = bootstrap_test_app()
        bus.handle(commands.AddActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=True))
        bus.handle(commands.AddEnrollmentPeriod(EnrollmentPeriodId=1, StartDate=date.today(), EndDate=date.today()+timedelta(days=30), NumEnrolled=0, ActivityId=1, ListPrice=100, Capacity=100))
        bus.handle(commands.EnrollStudent(StudentId=1, EnrollmentPeriodId=1, Balance=100, Price=100))
        # Would assert that an event gets spun up
        # Call to API and ensure that the item is queryable
        bus.handle(commands.ChangeStudentEnrollment(EnrollmentId=1, StudentId=1, EnrollmentPeriodId=1, Balance=0, Price=150))
        # Would assert that an event gets spun up
        # Call to API and ensure that the item is queryable
        bus.handle(commands.EnrollStudent(StudentId=1, EnrollmentPeriodId=2, Balance=100, Price=100))
        # Assert that it errored out since the enrollment period doesn't exist
        bus.handle(commands.ChangeActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=False))
        bus.handle(commands.EnrollStudent(StudentId=2, EnrollmentPeriodId=1, Balance=100, Price=100))
        # Assert that it errors out since the activity is not active

    def test_apply_payment(self):
        bus = bootstrap_test_app()
        bus.handle(commands.AddActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=True))
        bus.handle(commands.AddEnrollmentPeriod(EnrollmentPeriodId=1, StartDate=date.today(), EndDate=date.today()+timedelta(days=30), NumEnrolled=0, ActivityId=1, ListPrice=100, Capacity=100))
        bus.handle(commands.EnrollStudent(StudentId=1, EnrollmentPeriodId=1, Balance=100, Price=100))
        bus.handle(commands.ApplyPayment(EnrollmentId=1, PaymentAmount=100))
        # Would assert than an event got spun up that indicates that the payment was applied
        # Call API and query to see if payment was applied
        bus.handle(commands.ApplyPayment(EnrollmentId=1, PaymentAmount=100))
        # Assert that it errored out since the payment would have caused the balance to become negative

    def test_over_capacity(self):
        bus = bootstrap_test_app()
        bus.handle(commands.AddActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=True))
        bus.handle(commands.AddEnrollmentPeriod(EnrollmentPeriodId=1, StartDate=date.today(), EndDate=date.today()+timedelta(days=30), NumEnrolled=100, ActivityId=1, ListPrice=100, Capacity=100))
        bus.handle(commands.EnrollStudent(StudentId=1, EnrollmentPeriodId=1, Balance=100, Price=100))
        # assert that it failed because we would be over capacity



class TestActivityAndEnrollmentPeriods:
    def test_activity_crud(self):
        bus = bootstrap_test_app()
        bus.handle(commands.AddActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=True))
        # assert that the activity was added to the read model
        bus.handle(commands.ChangeActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test2', Active=True))
        # assert that the activity was updated in the read model
        bus.handle(commands.DeletedActivity(ActivityId=1))
        # assert that the activity was removed from the read model

    def test_enrollment_period_crud(self):
        bus = bootstrap_test_app()
        bus.handle(commands.AddActivity(ActivityId=1, Type='Sport', Name='Soccer', LeadByEmployeeId=1, Description='Test', Active=True))
        bus.handle(commands.AddEnrollmentPeriod(EnrollmentPeriodId=1, StartDate=date.today(), EndDate=date.today()+timedelta(days=30), NumEnrolled=0, ActivityId=1, ListPrice=100, Capacity=100))
        # assert that the enrollment period was updated in the read model
        bus.handle(commands.UpdateEnrollmentPeriod(EnrollmentPeriodId=1, StartDate=date.today(), EndDate=date.today()+timedelta(days=30), NumEnrolled=50, ActivityId=1, ListPrice=100, Capacity=100))
        # assert that the enrollment period was updated in the read model
        bus.handle(commands.RemoveEnrollmentPeriod(EnrollmentPeriodId=1))
        # assert that the enrollment period was removed

