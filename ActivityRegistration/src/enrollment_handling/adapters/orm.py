import logging

from sqlalchemy import Column, Integer, MetaData, String, Table, event, Float, Date, Time, Text, Boolean

# from sqlalchemy.orm import mapper
from sqlalchemy.orm import registry

from enrollment_handling.domain.models import Activity, Enrollment, EnrollmentPeriod

logger = logging.getLogger(__name__)

metadata = MetaData()

mapper_registry = registry()

activities_view = Table(
    'activities_view',
    mapper_registry.metadata,
    Column('Id', Integer),
    Column('Type', String(255)),
    Column('Name', String(255)),
    Column('LeadByEmployeeId', Integer),
    Column('Description', Text(255)),
    Column('Active', Boolean)
)

enrollments = Table(
    'enrollments',
    mapper_registry.metadata,
    Column('Id', Integer, primary_key=True, autoincrement=True),
    Column('StudentId', Integer),
    Column('EnrollmentPeriodId', Integer),
    Column('Balance', Float),
    Column('Price', Float),
)

enrollments_view = Table(
    'enrollments_view',
    mapper_registry.metadata,
    Column('Id', Integer),
    Column('StudentId', Integer),
    Column('EnrollmentPeriodId', Integer),
    Column('Balance', Float),
    Column('Price', Float),
)

enrollment_periods_view = Table(
    'enrollment_periods_view',
    mapper_registry.metadata,
    Column('Id', Integer),
    Column('StartDate', Date),
    Column('EndDate', Date),
    Column('ActivityId', Integer),
    Column('Capacity', Integer),
    Column('NumEnrolled', Integer),
    Column('ListPrice', Float),
)


def start_mappers():
    logger.info("string mappers")
    # SQLAlchemy 2.0
    activities_mapper = mapper_registry.map_imperatively(Activity, activities_view)
    enrollments_mapper = mapper_registry.map_imperatively(Enrollment, enrollments)
    enrollments_mapper = mapper_registry.map_imperatively(Enrollment, enrollments_view)
    enrollment_periods_mapper = mapper_registry.map_imperatively(EnrollmentPeriod, enrollment_periods_view)


@event.listens_for(Enrollment, "load")
def receive_enrollment_load(enrollment: Enrollment, _):
    enrollment.events = []

