from flask import Flask, jsonify, request
from enrollment_handling.domain import commands
from enrollment_handling.domain.models import InvalidEnrollmentId, InvalidEnrollmentPeriodId, InvalidActivityId,\
    MaxCapacityReached, ActivityNotActive
from enrollment_handling import bootstrap, views

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route('/enroll/add', method=['POST'])
def enrollment_add():
    try:
        cmd = commands.EnrollStudent(
            StudentId=request.json['StudentId'],
            EnrollmentPeriodId=request.json['EnrollmentPeriodId'],
            Balance=request.json['Balance'],
            Price=request.json['Price'],
        )
        bus.handle(cmd)
        return 'OK', 201

    except MaxCapacityReached as e:
        return {'message': str(e)}, 400
    except InvalidEnrollmentPeriodId as e:
        return {'message': str(e)}, 400
    except ActivityNotActive as e:
        return {'message': str(e)}, 400
    except InvalidActivityId as e:
        return {'message': str(e)}, 400
    except Exception as e:
        return {'message': 'An error occurred trying to enroll: ' + str(e)}, 400


@app.route('/enroll/<enrollment_id>/get', method=['GET'])
def enrollment_get(id):
    try:
        results = views.enrollments(id, uow=bus.uow)
        if results:
            return jsonify(results, 201)
        else:
            return {'message': f'No results were found for {id}'}, 404
    except InvalidEnrollmentId as e:
        return {'message': str(e)}, 400
    except Exception as e:
        return {'message': f'An error occurred while querying {id}:' + str(e)}, 401


@app.route('/enroll/<enrollment_id>/edit', method=['POST'])
def enrollment_edit(id):
    try:
        cmd = commands.ChangeStudentEnrollment(
            EnrollmentId=id,
            StudentId=request.json['StudentId'],
            EnrollmentPeriodId=request.json['EnrollmentPeriodId'],
            Balance=request.json['Balance'],
            Price=request.json['Price'],
        )
        bus.handle(cmd)
        return 'OK', 201
    except InvalidEnrollmentId as e:
        return {'message': str(e)}, 401
    except Exception as e:
        return {'message': f'An error occurred trying to modify the enrollment period {id}: {e}'}, 400
