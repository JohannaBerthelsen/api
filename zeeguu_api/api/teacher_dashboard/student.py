import datetime
from datetime import timedelta

import flask
from flask import jsonify
from sqlalchemy.orm.exc import NoResultFound

from zeeguu_core.model import User, Cohort
from .decorator import only_teachers
from .helpers import student_info_for_teacher_dashboard
from .permissions import (
    _abort_if_no_permission_for_cohort,
    _abort_if_no_permission_for_user,
    has_permission_for_cohort,
)
from .. import api
from ..utils.json_result import json_result
from ..utils.route_wrappers import with_session


@api.route("/cohort_member_bookmarks/<id>/<time_period>", methods=["GET"])
@with_session
@only_teachers
def cohort_member_bookmarks(id, time_period):

    user = User.query.filter_by(id=id).one()

    _abort_if_no_permission_for_cohort(user.cohort_id)

    now = datetime.today()
    date = now - timedelta(days=int(time_period))

    cohort_language_id = Cohort.query.filter_by(id=user.cohort_id).one().language_id

    # True input causes function to return context too.
    return json_result(
        user.bookmarks_by_day(
            True, date, with_title=True, max=10000, language_id=cohort_language_id
        )
    )


@api.route("/user_info/<id>/<duration>", methods=["GET"])
@with_session
def user_info_api(id, duration):

    _abort_if_no_permission_for_user(id)

    return jsonify(student_info_for_teacher_dashboard(id, duration))


@api.route("/cohort_member_reading_sessions/<id>/<time_period>", methods=["GET"])
@with_session
def cohort_member_reading_sessions(id, time_period):
    """
    Returns reading sessions from member with input user id.
    """
    try:
        user = User.query.filter_by(id=id).one()
    except NoResultFound:
        flask.abort(400)
        return "NoUserFound"

    if not has_permission_for_cohort(user.cohort_id):
        flask.abort(401)

    cohort = Cohort.query.filter_by(id=user.cohort_id).one()
    cohort_language_id = cohort.language_id

    now = datetime.today()
    date = now - timedelta(days=int(time_period))
    return json_result(
        user.reading_sessions_by_day(date, max=10000, language_id=cohort_language_id)
    )
