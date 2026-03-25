from fastapi import Request, Form, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import languages_collection
from helper_function.apis_requests import get_current_user
from datetime import datetime

async def create_language(
    request: Request,
    token: str = Depends(get_current_user),
    name: str = Form(None),
    status: bool = Form(None)
):
    """Create new language"""
    try:
        # Check if required fields are provided
        if not name:
            return JSONResponse({"message": "Name field is required"}, status_code=400)
        if status is None:
            status = True
        
        # Check if language already exists
        existing_language = await languages_collection.find_one({"name": name})
        if existing_language:
            return JSONResponse({"message": "Language with this name already exists"}, status_code=400)
        
        current_time = datetime.now()
        
        # Create new language
        new_language = {
            "name": name,
            "status": status,
            "createdAt": current_time
        }
        
        result = await languages_collection.insert_one(new_language)
        language_id = str(result.inserted_id)
        
        # Format response
        new_language["_id"] = language_id
        new_language["createdAt"] = new_language["createdAt"].isoformat()
        
        return {
            "success": True,
            "message": "Language created successfully",
            "data": new_language
        }
        
    except Exception as e:
        return JSONResponse({"message": f"Internal server error: {str(e)}"}, status_code=500)