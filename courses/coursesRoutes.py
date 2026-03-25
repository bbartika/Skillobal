from fastapi import APIRouter
from courses.views.course_curd.create_courses import create_course
# from courses.views.course_curd.all_courses_details import get_all_courses_details
from courses.views.course_curd.get_courses_list import get_courses_list
from courses.views.course_curd.visible_courses import get_visible_courses
from courses.views.course_curd.visible_T_F import toggle_course_visibility
from courses.views.course_curd.delete_entire_course import delete_entire_course

from courses.views.course_curd.update_course import update_course
from courses.views.course_curd.add_videos_to_course import add_videos_to_course
from courses.views.course_curd.update_course_video import update_course_video_by_fileid, delete_course_video_by_fileid
from courses.views.course_curd.specific_course_details import get_specific_course_details
from courses.views.course_curd.filtered_course_list import get_filtered_course_list


from documentation.userRoutesAPIDocumentation import *

courses_router = APIRouter(prefix="/admin", tags=["Courses"])

# Course CRUD
courses_router.add_api_route("/courses/add", create_course, methods=["POST"], description="Create new course")
# courses_router.add_api_route("/courses/list", get_all_courses_details, methods=["GET"], description="Get all courses with pagination")
courses_router.add_api_route("/courses/", get_courses_list, methods=["GET"], description="Get simplified course list")
courses_router.add_api_route("/coursesbyparam", get_filtered_course_list, methods=["GET"], description="Get filtered course list with visible=true")
courses_router.add_api_route("/courses/{course_id}/details", get_specific_course_details, methods=["GET"], description="Get specific course full details")
courses_router.add_api_route("/courses/visible", get_visible_courses, methods=["GET"], description="Get visible courses")

courses_router.add_api_route("/courses/{course_id}/update", update_course, methods=["PUT"], description="Update course with smart file replacement")
courses_router.add_api_route("/courses/{course_id}/videos/add", add_videos_to_course, methods=["POST"], description="Add videos to existing course")
courses_router.add_api_route("/courses/{course_id}/videos/{file_id}/update", update_course_video_by_fileid, methods=["PUT"], description="Update specific course video by fileId")
courses_router.add_api_route("/courses/{course_id}/videos/{file_id}/delete", delete_course_video_by_fileid, methods=["DELETE"], description="Delete specific course video by fileId")
courses_router.add_api_route("/courses/{course_id}/visibility/toggle", toggle_course_visibility, methods=["PUT"], description="Toggle course visibility")
courses_router.add_api_route("/courses/{course_id}/delete", delete_entire_course, methods=["DELETE"], description="Delete entire course and all media")






