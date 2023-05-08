import json
import logging
from datetime import date

import redis

from enrollment_handling import bootstrap, config
from enrollment_handling.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('activity_added_published',  # Notification that an activity has been published
                     'activity_updated_published',  # Notification that an activity has been updated
                     'activity_deleted_published',  # Notification that an activity has been canceled
                     'enrollment_period_added_published',  # Notification that an enrollment period has been added
                     'enrollment_period_updated_published',  # Notification that an enrollment period has been updated
                     'enrollment_period_removed_published',  # Notification that an enrollment period has been removed
                     'enrollment_payment_published',  # Notification that a payment has been published
                     )

    for m in pubsub.listen():
        proces_message(m, bus)


def proces_message(m, bus):
    match m.channel:
        case 'activity_added_published':
            handle_scheduled_activity_published('added', m, bus)
        case 'activity_updated_published':
            handle_scheduled_activity_published('updated', m, bus)
        case 'activity_deleted_published':
            handle_scheduled_activity_published('deleted', m, bus)
        case 'enrollment_period_added_published':
            handle_enrollment_period_published('added', m, bus)
        case 'enrollment_period_updated_published':
            handle_enrollment_period_published('updated', m, bus)
        case 'enrollment_period_deleted_published':
            handle_enrollment_period_published('deleted', m, bus)
        case 'enrollment_payment_published':
            handle_payment_published(m, bus)


def handle_scheduled_activity_published(pub_type, m, bus):
    data = json.loads(m['data'])
    cmd = None
    if pub_type is 'added':
        cmd = commands.AddActivity(
            ActivityId=int(data['ActivityId']),
            Active=bool(data['Active']),
            Description=data['Description'],
            LeadByEmployeeId=int(data['LeadByEmployeeId']),
            Name=data['Name'],
            Type=data['Type'],
        )
    if pub_type is 'updated':
        cmd = commands.ChangeActivity(
            ActivityId=int(data['ActivityId']),
            Active=bool(data['Active']),
            Description=data['Description'],
            LeadByEmployeeId=int(data['LeadByEmployeeId']),
            Name=data['Name'],
            Type=data['Type'],
        )
    if pub_type is 'deleted':
        cmd = commands.DeletedActivity(
            ActivityId=int(data['ActivityId'])
        )

    bus.handle(cmd)


def handle_enrollment_period_published(pub_type, m, bus):
    data = json.loads(m['data'])
    cmd = None
    if pub_type is 'added':
        cmd = commands.AddEnrollmentPeriod(
            EnrollmentPeriodId=int(data['EnrollmentPeriodId']),
            ActivityId=int(data['ActivityId']),
            Capacity=int(data['Capacity']),
            NumEnrolled=int(data['NumEnrolled']),
            ListPrice=int(data['ListPrice']),
            StartDate=date(data['StartDate']),
            EndDate=date(data['EndDate']),
        )
    if pub_type is 'updated':
        cmd = commands.UpdateEnrollmentPeriod(
            EnrollmentPeriodId=int(data['EnrollmentPeriodId']),
            ActivityId=int(data['ActivityId']),
            Capacity=int(data['Capacity']),
            NumEnrolled=int(data['NumEnrolled']),
            ListPrice=int(data['ListPrice']),
            StartDate=date(data['StartDate']),
            EndDate=date(data['EndDate']),
        )
    if pub_type is 'deleted':
        cmd = commands.RemoveEnrollmentPeriod(
            EnrollmentPeriodId=int(data['EnrollmentPeriodId']),
        )

    bus.handle(cmd)


def handle_payment_published(m, bus):
    data = json.loads(m['data'])
    cmd = commands.ApplyPayment(
        EnrollmentId=int(data['EnrollmentId']),
        PaymentAmount=float(data['PaymentAmount']),
    )
    bus.handle(cmd)


if __name__ == "__main__":
    main()
