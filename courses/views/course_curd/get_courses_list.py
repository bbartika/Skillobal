from fastapi import HTTPException, Request, Depends
from core.database import courses_collection
from helper_function.apis_requests import get_current_user

async def get_courses_list(
    request: Request,
    token: str = Depends(get_current_user),
    page: int = 1,
    limit: int = 10,
    search: str = None,
    visible: bool = None
):
    """Get simplified course list with pagination, search, and visibility filter"""
    try:
        skip = (page - 1) * limit
        
        # Build query filter
        query = {}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        if visible is not None:
            query["visible"] = visible
        
        # Get total count
        total_courses = await courses_collection.count_documents(query)
        
        # Get paginated courses
        courses_cursor = courses_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        courses = await courses_cursor.to_list(length=None)
        
        courses_list = []
        for course in courses:
            course_data = {
                "_id": str(course["_id"]),
                "title": course.get("title", ""),
                "description": course.get("description", ""),
                "enrolled": 0,
                "rating": course.get("rating", 0),
                "skills": course.get("skills", []),
                "price": course.get("price", 0),
                "visible": course.get("visible", False),
                "intro_video": course.get("intro_videos", {}).get("videoUrl", "") if course.get("intro_videos") else "",
                "image_url": course.get("images", {}).get("course_image_url", "") if course.get("images") else ""
            }
            courses_list.append(course_data)
        
        total_pages = (total_courses + limit - 1) // limit
        
        return {
            "success": True,
            "message": f"Retrieved {len(courses_list)} courses successfully",
            "data": courses_list,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_courses": total_courses,
                "limit": limit
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Something went wrong while fetching courses"
        }
