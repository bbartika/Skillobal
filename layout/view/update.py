from fastapi import HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import db, courses_collection
from helper_function.apis_requests import get_current_user
from datetime import datetime
from typing import List, Optional

layout_collection = db['layout']

async def update_layout(
    layout_id: str,
    request: Request,
    token: str = Depends(get_current_user),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    course_id: Optional[List[str]] = Form(None),
    status: Optional[bool] = Form(None)
):
    """Update layout"""
    try:
        # Validate layout_id
        if not ObjectId.is_valid(layout_id):
            return JSONResponse({"message": "Invalid layout ID"}, status_code=400)
        
        # Check if layout exists
        existing_layout = await layout_collection.find_one({'_id': ObjectId(layout_id)})
        if not existing_layout:
            return JSONResponse({"message": "Layout not found"}, status_code=404)
        
        # Format existing layout for response
        existing_layout['_id'] = str(existing_layout['_id'])
        if 'createdAt' in existing_layout:
            existing_layout['createdAt'] = existing_layout['createdAt'].isoformat()
        if 'updatedAt' in existing_layout:
            existing_layout['updatedAt'] = existing_layout['updatedAt'].isoformat()
        
        # Build update document with optional fields
        update_doc = {'updatedAt': datetime.now()}
        
        if title is not None:
            # Check if title already exists (excluding current layout)
            existing_title = await layout_collection.find_one({
                'title': title,
                '_id': {'$ne': ObjectId(layout_id)}
            })
            if existing_title:
                return JSONResponse({"message": "Layout with this title already exists"}, status_code=400)
            update_doc['title'] = title
        if description is not None:
            update_doc['description'] = description
        if course_id is not None:
            # Remove this layout from all courses first
            await courses_collection.update_many(
                {'layout_id': ObjectId(layout_id)},
                {'$pull': {'layout_id': ObjectId(layout_id)}}
            )
            
            # Add this layout to specified courses
            if course_id:  # Only if course_id list is not empty
                course_object_ids = [ObjectId(cid) for cid in course_id]
                await courses_collection.update_many(
                    {'_id': {'$in': course_object_ids}},
                    {'$addToSet': {'layout_id': ObjectId(layout_id)}}
                )
        if status is not None:
            update_doc['status'] = status
        
        # Update layout
        await layout_collection.update_one(
            {'_id': ObjectId(layout_id)},
            {'$set': update_doc}
        )
        
        # Get updated layout
        updated_layout = await layout_collection.find_one({'_id': ObjectId(layout_id)})
        
        # Format response
        updated_layout['_id'] = str(updated_layout['_id'])
        if 'createdAt' in updated_layout:
            updated_layout['createdAt'] = updated_layout['createdAt'].isoformat()
        if 'updatedAt' in updated_layout:
            updated_layout['updatedAt'] = updated_layout['updatedAt'].isoformat()
        
        return {
            'success': True,
            'message': 'Layout updated successfully'
        }
        
    except Exception as e:
        return JSONResponse({"message": f"Internal server error: {str(e)}"}, status_code=500)