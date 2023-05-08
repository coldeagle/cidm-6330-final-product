from enrollment_handling.service_layer import unit_of_work
from sqlalchemy.sql import text


def enrollments(id: int, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text('SELECT Id, StudentId, EnrollmentPeriodId, Balance, Price FROM enrollments_view WHERE Id = :id', dict(id=id))
        )

    return_list = list()
    for r in results:
        return_list.append(dict(Id=r[0], StudentId=r[1], EnrollmentPeriodId=r[2], Balance=r[3], Price=r[4]))

    return return_list


def enrollment_periods(id: int, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text('SELECT Id, StartDate, EndDate, ActivityId, Capacity, NumEnrolled, ListPrice FROM enrollment_periods_view WHERE Id = :id', dict(id=id))
        )

    return_list = list()

    for r in results:
        return_list.append(
            dict(Id=r[0], StartDate=r[1], EndDate=r[2], ActivityId=r[3], Capacity=r[4], NumEnrolled=r[5], ListPrice=r[6])
        )

    return return_list


def activities(id: int, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            text('SELECT Id, Type, Name, LeadByEmployeeId, Description, Active FROM activities_view WHERE Id = :id', dict(id=id))
        )

    return_list = list()

    for r in results:
        return_list.append(
            dict(Id=r[0], Type=r[1], Name=r[2], LeadByEmployeeId=r[3], Description=r[4], Active=r[5])
        )

    return return_list
