from datetime import date
from typing import Optional
from dataclasses import dataclass


class Command:
    pass


@dataclass
class AddActivity(Command):
    ActivityId: int
    Type: str
    Name: str
    LeadByEmployeeId: int
    Description: Optional[str]
    Active: bool = True


@dataclass
class ChangeActivity(Command):
    ActivityId: int
    Active: Optional[bool]
    Description: Optional[str]
    Type: Optional[str] = None
    Name: Optional[str] = None
    LeadByEmployeeId: Optional[int] = None


@dataclass
class DeletedActivity(Command):
    ActivityId: int


@dataclass
class EnrollStudent(Command):
    StudentId: int
    EnrollmentPeriodId: int
    Balance: float
    Price: float


@dataclass
class ChangeStudentEnrollment(Command):
    EnrollmentId: int
    StudentId: Optional[int] = None
    EnrollmentPeriodId: Optional[int] = None
    Balance: Optional[float] = None
    Price: Optional[float] = None


@dataclass
class ApplyPayment(Command):
    EnrollmentId: int
    PaymentAmount: float


@dataclass
class AddEnrollmentPeriod(Command):
    EnrollmentPeriodId: int
    StartDate: date
    EndDate: date
    ActivityId: int
    Capacity: int
    ListPrice: float
    NumEnrolled: int


@dataclass
class RemoveEnrollmentPeriod(Command):
    EnrollmentPeriodId: int


@dataclass
class UpdateEnrollmentPeriod(Command):
    EnrollmentPeriodId: int
    StartDate: date
    EndDate: date
    ActivityId: int
    Capacity: int
    NumEnrolled: int
    ListPrice: float
#
#
# @dataclass
# class AddScheduledActivity(Command):
#     EnrollmentPeriodId: int
#     Date: date
#     StartTime: time
#     EndTime: time
#
# @dataclass
# class ChangeScheduledActivity(Command):
#     ScheduledActivityId: int
#     Date: Optional[date] = None
#     StartTime: Optional[time] = None
#     EndTime: Optional[time] = None
#
