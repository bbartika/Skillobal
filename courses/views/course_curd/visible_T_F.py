from fastapi import HTTPException, Request, Depends, BackgroundTasks
from bson import ObjectId
from core.database import courses_collection
from helper_function.apis_requests import get_current_user
from core.cache import invalidate_course_cache
from datetime import datetime

async def toggle_course_visibility(
    course_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    token: str = Depends(get_current_user)
):
    """Toggle course visibility between true and false"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID format")
        
        object_id = ObjectId(course_id)
        
        # Use atomic operation to toggle visibility
        result = await courses_collection.find_one_and_update(
            {"_id": object_id},
            [
                {
                    "$set": {
                        "visible": {"$not": "$visible"},
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            ],
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Invalidate cache in background
        background_tasks.add_task(invalidate_course_cache, course_id)
        
        new_visible = result.get("visible", False)
        
        return {
            "success": True,
            "message": "Course is now visible" if new_visible else "Course is now hidden",
            "data": {
                "course_id": course_id,
                "current_visible": new_visible
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to toggle visibility")