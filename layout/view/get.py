from fastapi import HTTPException, Request, Depends
from bson import ObjectId
from core.database import db, courses_collection
from helper_function.apis_requests import get_current_user

layout_collection = db['layout']

async def get_all_layouts(
    request: Request,
    token: str = Depends(get_current_user),
    page: int = 1,
    limit: int = 10
):
    """Get all layouts with pagination"""
    try:
        skip = (page - 1) * limit
        
        # Get total count
        total_layouts = await layout_collection.count_documents({})
        
        # Get paginated layouts sorted by latest first
        docs_cursor = layout_collection.find({}).sort("_id", -1).skip(skip).limit(limit)
        docs = await docs_cursor.to_list(length=None)
        
        layouts = []
        for doc in docs:
            layout_id = doc.get("_id")
            
            # Find all courses that use this layout ID
            courses_with_layout = await courses_collection.find(
                {"layout_id": layout_id}
            ).to_list(length=None)
            
            course_ids = [str(course["_id"]) for course in courses_with_layout]
            
            layouts.append({
                "id": str(layout_id),
                "title": doc.get("title"),
                "description": doc.get("description"),
                "course_id": course_ids,
                "status": doc.get("status", True)
            })
        
        total_pages = (total_layouts + limit - 1) // limit
        
        return {
            "success": True,
            "message": f"Retrieved {len(layouts)} layouts successfully",
            "data": layouts,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_layouts": total_layouts,
                "limit": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))