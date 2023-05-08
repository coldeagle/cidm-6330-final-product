import abc
from typing import Set

from sqlalchemy import desc

from enrollment_handling.adapters import orm
from enrollment_handling.domain import models
from enrollment_handling.domain.models import Enrollment


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[Enrollment]

    def add(self, enrollment: Enrollment):
        self._add(enrollment)
        self.seen.add(enrollment)

    def get(self, id: int) -> Enrollment:
        enrollment = self._get(id)
        if enrollment:
            self.seen.add(enrollment)
        return enrollment

    def get_by_student_and_enrollment_period(self, student_id: int, enrollment_period_id: int) -> Enrollment:
        enrollment = self._get_by_student_and_enrollment_period(
            student_id=student_id,
            enrollment_period_id=enrollment_period_id
        )
        if enrollment:
            self.seen.add(enrollment)
        return enrollment

    @abc.abstractmethod
    def _add(self, enrollment: Enrollment):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, id) -> Enrollment:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_student_and_enrollment_period(self, student_id: int, enrollment_period_id: int) -> Enrollment:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, enrollment: Enrollment):
        self.session.add(enrollment)

    def _get(self, id: int):
        return self.session.query(Enrollment).filter_by(id=id).first()

    def _get_by_student_and_enrollment_period(self, student_id: int, enrollment_period_id: int):
        return self.session.query(
            models.Enrollment).filter(
                orm.enrollments.c.StudentId == student_id,
                orm.enrollments.c.EnrollmentPeriodId == enrollment_period_id
            ).order_by(
                desc(orm.enrollments.c.Id)
            ).first()
