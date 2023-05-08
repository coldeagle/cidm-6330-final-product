from __future__ import annotations
from datetime import date
from typing import Optional
from enrollment_handling.domain import events


class Activity:
    Id: int
    Type: str
    Name: str
    LeadByEmployeeId: int
    Description: str
    Active: bool

    def __init__(self,
                 id: Optional[int],
                 type: str,
                 name: str,
                 lead_by_employee_id: int,
                 description: str,
                 active: bool):

        if active is None:
            active = True

        self.Id = id
        self.Type = type
        self.Name = name
        self.LeadByEmployeeId = lead_by_employee_id
        self.Description = description
        self.Active = active


class Enrollment:
    Id: int
    StudentId: int
    EnrollmentPeriodId: int
    Balance: float
    Price: float
    Events: list

    def __init__(self,
                 id: Optional[int],
                 student_id: int,
                 enrollment_period_id: int,
                 balance: float,
                 price: float):

        self.Id = id
        self.StudentId = student_id
        self.EnrollmentPeriodId = enrollment_period_id
        self.Balance = balance
        self.Price = price
        self.Events = list()

    def handle_insert(self):
        self.Events.append(
            events.NewEnrollment(
                StudentId=self.StudentId,
                EnrollmentId=self.Id,
                EnrollmentPeriodId=self.EnrollmentPeriodId,
                Balance=self.Balance,
                Price=self.Price
            )
        )

    def apply_payment(self, payment_amount: float):
        if self.Balance - payment_amount < 0:
            raise PaymentGreaterThanBalance(f'{payment_amount} is more than the balance of {self.Balance}!')
        else:
            self.Balance = self.Balance - payment_amount


class EnrollmentPeriod:
    Id: int
    StartDate: date
    EndDate: date
    ActivityId: int
    Capacity: int
    NumEnrolled: int
    ListPrice: float

    def __init__(self,
                 id: Optional[int],
                 start_date: date,
                 end_date: date,
                 activity_id: int,
                 capacity: int,
                 num_enrolled: Optional[int],
                 list_price: float):

        self.Id = id
        self.StartDate = start_date
        self.EndDate = end_date
        self.ActivityId = activity_id
        self.Capacity = capacity
        self.NumEnrolled = num_enrolled
        self.ListPrice = list_price


class MaxCapacityReached(Exception):
    pass


class PaymentGreaterThanBalance(Exception):
    pass


class ActivityNotActive(Exception):
    pass


class InvalidActivityId(Exception):
    pass


class InvalidEnrollmentPeriodId(Exception):
    pass


class InvalidEnrollmentId(Exception):
    pass


class StudentAlreadyEnrolled(Exception):
    pass


class StudentEnrollmentNotFound(Exception):
    pass
