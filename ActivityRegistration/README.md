# CIDM 6330 - Final - Hardy
This is a module designed to work along with an student portal that enables people to log in, 
verify what they are enrolled in, enroll into activities, see activity schedules, pay for activities. 

This specific module would allow users to enroll into activities. 

It would subscribe to messages from other modules, specifically activity (which are the types of activities available) 
and the enrollment period (which covers the specific "class" for that activity). For example the activity could be
"soccor" and the enrollment period would be for 4/1 to 5/1. The student would enroll into the activity for 
that specific enrollment period. It also subscribes to payments being applied to the specific enrollment. The
blanace for the enrollment is tracked there. Anytime there is an update made to the enrollment record an event
is publisehd that pushes the updates to other modules so the information about enrollments are kept up-to-date.
## API
There are three APIs available for this module. All are called with the base "enroll":
### add (post) 

It will add the enrollment record. It has the following properties:
* EnrollmentPeriodId
* StudentId
* Price
* Balance

When called, it will check:
* Does the enrollment period exist?
* Is the enrollment period's connected activity active?
### enrollment_id/edit (post)
It will edit the enrollment record. It has the same properties as add and the id of the record
is added as a part of the URL 
### enrollment_id/get (get)
It will retrieve the enrollment record. The Id of the record being queried is passed as a part of the 
URL.

## Events
### Publish
It will publish the following events:
* payment_applied: Sends an event notifying subscribers that a payment has been applied
* student_enrollment_change: Sends an event notifying subscribers that an enrollment has been updated
* new_student_enrollment: Sends an event notifying subscribers that a new student enrollment has taken place

### Consume
It will consume the following events:
* activity_added_published: When an activity is added
* activity_updated_published: When an activity is updated
* activity_deleted_published: When an activity is deleted
* enrollment_period_added_published: When an enrollment period is added
* enrollment_period_updated_published: When an enrollment period is updated
* enrollment_period_deleted_published: When an enrollment period is deleted
* enrollment_payment_published: When a payment has been processed for an enrollment 