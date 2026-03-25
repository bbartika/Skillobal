from fastapi import APIRouter
from instructors.views.get_instructors import get_all_instructors

router = APIRouter(prefix="/admin/instructors", tags=["Instructors"])

# Instructor operations
router.add_api_route("/", get_all_instructors, methods=["GET"], description="Get all instructors")