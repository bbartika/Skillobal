from fastapi import Request, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import categories_collection
from helper_function.image_upload import upload_image_to_tencent
from helper_function.apis_requests import get_current_user
from datetime import datetime
from typing import Optional

async def create_category(
    request: Request,
    token: str = Depends(get_current_user),
    name: Optional[str] = Form(None),
    category_image: Optional[UploadFile] = File(None),
    status: Optional[bool] = Form(None)
):
    """Create new category with image upload to Tencent Cloud"""
    try:
        # Check if required fields are provided
        if not name:
            return JSONResponse({"message": "Name field is required"}, status_code=400)
        if not category_image:
            return JSONResponse({"message": "Category image field is required"}, status_code=400)
        if status is None:
            status = True
        
        # Check if category already exists
        existing_category = await categories_collection.find_one({"name": name})
        if existing_category:
            return JSONResponse({"message": "Category with this name already exists"}, status_code=400)
        
        current_time = datetime.now()
        
        # Upload image to Tencent Cloud
        image_content = await category_image.read()
        image_result = await upload_image_to_tencent(image_content, category_image.filename)
        
        # Create image object
        image_obj = {
            "fileId": image_result["file_id"],
            "image_url": image_result["image_url"]
        }
        
        # Create new category  
        new_category = {
            "name": name,
            "image": image_obj,
            "status": status,
            "createdAt": current_time
        }
        
        result = await categories_collection.insert_one(new_category)
        category_id = str(result.inserted_id)
        
        # Format response
        new_category["_id"] = category_id
        new_category["createdAt"] = new_category["createdAt"].isoformat()
        
        return {
            "success": True,
            "message": "Category created successfully",
            "data": new_category
        }
        
    except Exception as e:
        return JSONResponse({"message": f"Internal server error: {str(e)}"}, status_code=500)