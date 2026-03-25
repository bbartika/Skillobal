from fastapi import Request, Form, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import languages_collection
from helper_function.apis_requests import get_current_user
from datetime import datetime
from typing import Optional

async def update_language(
    language_id: str,
    request: Request,
    token: str = Depends(get_current_user),
    name: Optional[str] = Form(None),
    status: Optional[bool] = Form(None)
):
    """Update language with optional name and status change"""
    try:
        if not ObjectId.is_valid(language_id):
            return JSONResponse({"message": "Invalid language ID format"}, status_code=400)
        
        # Check if language exists
        existing_language = await languages_collection.find_one({"_id": ObjectId(language_id)})
        if not existing_language:
            return JSONResponse({"message": "Language not found"}, status_code=404)
        
        # Check if at least one field is provided for update
        if not name and status is None:
            return JSONResponse({"message": "No data provided for update"}, status_code=400)
        
        # Prepare update data
        update_data = {"updatedAt": datetime.now()}
        
        # Update name if provided
        if name:
            # Check if new name already exists (excluding current language)
            name_exists = await languages_collection.find_one({
                "name": name,
                "_id": {"$ne": ObjectId(language_id)}
            })
            if name_exists:
                return JSONResponse({"message": "Language with this name already exists"}, status_code=400)
            update_data["name"] = name
        
        # Update status if provided
        if status is not None:
            update_data["status"] = status
        
        # Update language in database
        result = await languages_collection.update_one(
            {"_id": ObjectId(language_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return JSONResponse({"message": "Language not found"}, status_code=404)
        
        # Get updated language
        updated_language = await languages_collection.find_one({"_id": ObjectId(language_id)})
        
        # Format response
        updated_language["_id"] = str(updated_language["_id"])
        updated_language["createdAt"] = updated_language["createdAt"].isoformat()
        updated_language["updatedAt"] = updated_language["updatedAt"].isoformat()
        
        return {
            "success": True,
            "message": "Language updated successfully",
            "data": updated_language
        }
        
    except Exception as e:
        return JSONResponse({"message": f"Internal server error: {str(e)}"}, status_code=500)