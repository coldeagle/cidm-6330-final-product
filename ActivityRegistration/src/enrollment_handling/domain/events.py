from dataclasses import dataclass


class Event:
    pass


@dataclass
class NewEnrollment(Event):
    EnrollmentId: int
    StudentId: int
    EnrollmentPeriodId: int
    Balance: float
    Price: float


@dataclass
class EnrollmentChanged(Event):
    EnrollmentId: int
    StudentId: int
    EnrollmentPeriodId: int
    Balance: float
    Price: float


@dataclass
class PaymentApplied(Event):
    EnrollmentId: int
    PaymentAmount: float
    Balance: float
