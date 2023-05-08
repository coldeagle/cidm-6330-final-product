# pylint: disable=unused-argument
from __future__ import annotations
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from enrollment_handling import views
from enrollment_handling.domain import commands, events, models
from enrollment_handling.domain.models import StudentAlreadyEnrolled, InvalidEnrollmentPeriodId, InvalidActivityId,\
    StudentEnrollmentNotFound, ActivityNotActive, MaxCapacityReached
from sqlalchemy import text

if TYPE_CHECKING:
    from enrollment_handling.adapters import notifications
    from . import unit_of_work


# noinspection SqlDialectInspection
def cmd_activity_add_to_read_model(
        cmd: commands.AddActivity,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        # noinspection SqlNoDataSourceInspection
        uow.session.execute(
            text('INSERT INTO activities_view (Id, Type, Name, LeadByEmployeeId, Description, Active) '
                 'VALUES(:id, :type, :name, :lead_by, :desc, :active)',
                 dict(id=cmd.ActivityId,
                      type=cmd.Type,
                      name=cmd.Name,
                      lead_by=cmd.LeadByEmployeeId,
                      desc=cmd.Description,
                      active=True)
                 )
        )
        uow.commit()


# noinspection SqlDialectInspection
def cmd_activity_remove_from_read_model(
        cmd: commands.DeletedActivity,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text('DELETE FROM activities_view WHERE id=:id',
                 dict(id=cmd.ActivityId)),
        )


# noinspection SqlDialectInspection
def cmd_activity_update_to_read_model(
        cmd: commands.ChangeActivity,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text('UPDATE activities_view '
                 'SET (Type = :type, Name = :name, LeadByEmployeeId = :lead_by, Description = :desc, Active=:active) '
                 'WHERE Id = :id',
                 dict(id=cmd.ActivityId,
                      type=cmd.Type,
                      name=cmd.Name,
                      lead_by=cmd.LeadByEmployeeId,
                      desc=cmd.Description,
                      active=cmd.Active)
                 )
        )
        uow.commit()


def cmd_enrollment_apply_payment(
        cmd: commands.ApplyPayment,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        enrollment = uow.enrollments.get(id=cmd.EnrollmentId)
        if enrollment is not None:
            enrollment.apply_payment(payment_amount=cmd.PaymentAmount)
            uow.commit()
        else:
            raise InvalidEnrollmentPeriodId(f'{cmd.EnrollmentId} could not be located')


# noinspection SqlNoDataSourceInspection
def cmd_enrollment_enroll_student(
        cmd: commands.EnrollStudent,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        queried_enrollment = uow.enrollments.get_by_student_and_enrollment_period(cmd.StudentId, cmd.EnrollmentPeriodId)

        if queried_enrollment is not None:
            raise StudentAlreadyEnrolled(f'The student with Id {cmd.StudentId} has already been enrolled in {cmd.EnrollmentPeriodId}')
        enrollment_period = views.enrollment_periods(id=cmd.EnrollmentPeriodId, uow=uow)
        activity = views.activities(enrollment_period.ActivityId)

        enrollment = models.Enrollment(
            student_id=cmd.StudentId,
            enrollment_period_id=cmd.EnrollmentPeriodId,
            balance=cmd.Balance,
            price=cmd.Price
        )
        enrollment_insert_check(enrollment=enrollment, enrollment_period=enrollment_period, activity=activity)
        uow.enrollments.add(enrollment)
        uow.commit()

        queried_enrollment = uow.enrollments.get_by_student_and_enrollment_period(cmd.StudentId, cmd.EnrollmentPeriodId)
        if queried_enrollment is None:
            raise StudentEnrollmentNotFound('Student enrollment was not successful, it could not be found after insertion!')
        else:
            enrollment.handle_insert()
            # noinspection SqlDialectInspection
            uow.session.execute(
                text('INSERT INTO enrollments_view (Id, StudentId, EnrollmentPeriodId, Balance, Price) '
                     'VALUES(:id, :student_id, :enrollment_period_id, :balance, :price)',
                     dict(id=queried_enrollment.Id,
                          student_id=cmd.StudentId,
                          enrollment_period_id=cmd.EnrollmentPeriodId,
                          balance=cmd.Balance,
                          price=cmd.Price
                          )
                     )
            )
            uow.commit()


def enrollment_insert_check(enrollment: models.Enrollment, enrollment_period: models.EnrollmentPeriod, activity: models.Activity):
    if enrollment_period is not None:
        if enrollment_period.NumEnrolled + 1 > enrollment_period.Capacity:
            raise MaxCapacityReached(f'There is no more capacity in enrollment period {enrollment_period.Id}')
        if activity is None:
            raise InvalidActivityId('A valid activity id was not located')
        elif not activity.Active:
            raise ActivityNotActive(f'{activity.Id} is not active')
    else:
        raise InvalidEnrollmentPeriodId(f'{enrollment.EnrollmentPeriodId} is not a valid enrollment period id')


def cmd_enrollment_update(
        cmd: commands.ChangeStudentEnrollment,
        uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        enrollment = uow.enrollments.get(id=cmd.EnrollmentId)
        if enrollment is not None:
            if cmd.StudentId is not None:
                enrollment.StudentId = cmd.StudentId
            if cmd.EnrollmentPeriodId is not None:
                enrollment.EnrollmentPeriodId = cmd.EnrollmentPeriodId
            if cmd.Price is not None:
                enrollment.Price = cmd.Price
            if cmd.Balance is not None:
                enrollment.Balance = cmd.Balance
            uow.session.execute(
                text('UPDATE enrollments_view '
                     'SET (StudentId=:student_id, EnrollmentPeriodId=:enrollment_period_id, Balance=:balance, Price=:price) '
                     'WHERE Id = :id',
                     dict(id=enrollment.Id,
                          student_id=enrollment.StudentId,
                          enrollment_period_id=enrollment.EnrollmentPeriodId,
                          balance=enrollment.Balance,
                          price=enrollment.Price
                          )
                     )
            )
            uow.commit()
        else:
            raise InvalidEnrollmentPeriodId(f'{cmd.EnrollmentId} could not be located')


def cmd_enrollment_period_add_to_read_model(
        cmd: commands.AddEnrollmentPeriod,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(

            text('INSERT INTO enrollment_periods_view (StartDate, EndDate, ActivityId, Capacity, NumEnrolled, ListPrice) '
                 'VALUES(:start_date, :end_date, :activity_id, :capacity, :num_enrolled, :list_price)',
                 dict(start_date=cmd.StartDate,
                      end_date=cmd.EndDate,
                      ActivityId=cmd.ActivityId,
                      Capacity=cmd.Capacity,
                      NumEnrolled=cmd.NumEnrolled,
                      list_price=cmd.ListPrice)
                 )
        )
        uow.commit()


def cmd_enrollment_period_remove_from_read_model(
        cmd: commands.RemoveEnrollmentPeriod,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text('DELETE FROM enrollment_periods_view WHERE id=:id', dict(id=cmd.EnrollmentPeriodId)),
        )


def cmd_enrollment_period_update_to_read_model(
        cmd: commands.UpdateEnrollmentPeriod,
        uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            text('UPDATE enrollment_periods_view '
                 'SET (StartDate = :start_date, EndDate = :end_date, ActivityId = :activity_id, Capacity = :capacity, NumEnrolled=:num_enrolled, ListPrice=:list_price) '
                 'WHERE Id = :id',
                 dict(id=cmd.EnrollmentPeriodId,
                      start_date=cmd.StartDate,
                      end_date=cmd.EndDate,
                      ActivityId=cmd.ActivityId,
                      Capacity=cmd.Capacity,
                      NumEnrolled=cmd.NumEnrolled,
                      list_price=cmd.ListPrice)
                 )
        )
        uow.commit()


def publish_payment_applied(
        event: events.PaymentApplied,
        publish: Callable
):
    publish('payment_applied', event)


def publish_student_enrollment_changed(
        event: events.EnrollmentChanged,
        publish: Callable
):
    publish('student_enrollment_change', event)


def publish_student_enrolled_event(
        event: events.NewEnrollment,
        publish: Callable,
):
    publish('new_student_enrollment', event)


EVENT_HANDLERS = {
    events.EnrollmentChanged: [publish_student_enrollment_changed],
    events.NewEnrollment: [publish_student_enrolled_event],
    events.PaymentApplied: [publish_payment_applied],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.AddActivity: cmd_activity_add_to_read_model,
    commands.AddEnrollmentPeriod: cmd_enrollment_period_add_to_read_model,
    commands.ApplyPayment: cmd_enrollment_apply_payment,
    commands.ChangeActivity: cmd_activity_update_to_read_model,
    commands.ChangeStudentEnrollment: cmd_enrollment_update,
    commands.DeletedActivity: cmd_activity_remove_from_read_model,
    commands.EnrollStudent: cmd_enrollment_enroll_student,
    commands.RemoveEnrollmentPeriod: cmd_enrollment_period_remove_from_read_model,
    commands.UpdateEnrollmentPeriod: cmd_enrollment_period_update_to_read_model,
}  # type: Dict[Type[commands.Command], Callable]
