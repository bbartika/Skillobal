from fastapi import HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import db, courses_collection
from helper_function.apis_requests import get_current_user
from datetime import datetime
from typing import List, Optional

layout_collection = db['layout']

async def create_layout(
    request: Request,
    token: str = Depends(get_current_user),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    course_id: Optional[List[str]] = Form(None),
    status: Optional[bool] = Form(None)
):
    """Create new layout"""
    try:
        # Check if required fields are provided
        if not title:
            return JSONResponse({"message": "Title field is required"}, status_code=400)
        if not description:
            return JSONResponse({"message": "Description field is required"}, status_code=400)
        
        # Check if title already exists
        existing_layout = await layout_collection.find_one({'title': title})
        if existing_layout:
            return JSONResponse({"message": "Layout with this title already exists"}, status_code=400)
        
        current_time = datetime.now()
        
        # Create layout document without course_id
        layout_doc = {
            'title': title,
            'description': description,
            'status': status,
            'createdAt': current_time
        }
        
        # Insert into database
        result = await layout_collection.insert_one(layout_doc)
        layout_object_id = result.inserted_id
        
        # Update courses with this layout_id if course_id provided
        if course_id:
            course_object_ids = [ObjectId(cid) for cid in course_id]
            await courses_collection.update_many(
                {'_id': {'$in': course_object_ids}},
                {'$addToSet': {'layout_id': layout_object_id}}
            )
        
        return {
            'success': True,
            'message': 'Layout created successfully',
            'data': {
                'id': str(result.inserted_id),
                'title': title,
                'description': description,
                'course_id': course_id or [],
                'status': status
            }
        }
        
    except Exception as e:
        return JSONResponse({"message": f"Internal server error: {str(e)}"}, status_code=500)