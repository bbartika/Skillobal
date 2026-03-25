from fastapi import HTTPException, Request, Depends
from bson import ObjectId
from core.database import db, courses_collection
from helper_function.apis_requests import get_current_user

layout_collection = db['layout']

async def delete_layout(
    layout_id: str,
    request: Request,
    token: str = Depends(get_current_user)
):
    """Delete layout"""
    try:
        # Validate layout_id
        if not ObjectId.is_valid(layout_id):
            raise HTTPException(status_code=400, detail={'message': 'Invalid layout ID'})
        
        # Check if layout exists
        existing_layout = await layout_collection.find_one({'_id': ObjectId(layout_id)})
        if not existing_layout:
            raise HTTPException(status_code=404, detail={'message': 'Layout not found'})
        
        # Remove layout_id from all courses first
        await courses_collection.update_many(
            {'layout_id': ObjectId(layout_id)},
            {'$pull': {'layout_id': ObjectId(layout_id)}}
        )
        
        # Delete layout
        await layout_collection.delete_one({'_id': ObjectId(layout_id)})
        
        return {
            'success': True,
            'message': 'Layout deleted successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'message': 'Failed to delete layout'})