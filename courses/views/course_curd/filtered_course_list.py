from fastapi import HTTPException, Request, Depends, Response
from typing import Optional
from bson import ObjectId
from core.database import courses_collection
from helper_function.apis_requests import get_current_user

async def get_filtered_course_list(
    request: Request,
    response: Response,
    token: str = Depends(get_current_user),
    category_id: Optional[str] = None,
    language_id: Optional[str] = None,
    slider_id: Optional[str] = None,
    layout_id: Optional[str] = None,
    course_id: Optional[str] = None
):
    """Get filtered course list with visible=true only"""
    try:
        # Build filter query
        filter_query = {"visible": True}
        
        # Validate and add filters
        if category_id:
            if not ObjectId.is_valid(category_id):
                response.status_code = 400
                return {
                    "success": False,
                    "message": "Invalid filter parameters"
                }
            filter_query["category_id"] = ObjectId(category_id)
        
        if language_id:
            if not ObjectId.is_valid(language_id):
                response.status_code = 400
                return {
                    "success": False,
                    "message": "Invalid filter parameters"
                }
            filter_query["language_id"] = ObjectId(language_id)
        
        if slider_id:
            if not ObjectId.is_valid(slider_id):
                response.status_code = 400
                return {
                    "success": False,
                    "message": "Invalid filter parameters"
                }
            filter_query["slider_id"] = ObjectId(slider_id)
        
        if layout_id:
            if not ObjectId.is_valid(layout_id):
                response.status_code = 400
                return {
                    "success": False,
                    "message": "Invalid filter parameters"
                }
            filter_query["layout_id"] = ObjectId(layout_id)
        
        if course_id:
            if not ObjectId.is_valid(course_id):
                response.status_code = 400
                return {
                    "success": False,
                    "message": "Invalid filter parameters"
                }
            filter_query["_id"] = ObjectId(course_id)
        
        # Fetch filtered courses
        courses_cursor = courses_collection.find(filter_query).sort("created_at", -1)
        courses = await courses_cursor.to_list(length=None)
        
        if not courses:
            response.status_code = 404
            return {
                "success": False,
                "message": "No courses found for given filters"
            }
        
        # Format response
        courses_list = []
        for course in courses:
            course_data = {
                "id": str(course["_id"]),
                "title": course.get("title", ""),
                "course_image_url": course.get("images", {}).get("course_image_url", "") if course.get("images") else "",
                "visible": course.get("visible", True)
            }
            courses_list.append(course_data)
        
        return {
            "success": True,
            "message": "Filtered course list fetched successfully",
            "data": courses_list
        }
        
    except Exception as e:
        response.status_code = 500
        return {
            "success": False,
            "message": "Something went wrong while fetching filtered courses"
        }
