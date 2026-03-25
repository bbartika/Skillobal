from fastapi import HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from core.database import db, courses_collection, sliders_collection
from helper_function.image_upload import upload_image_to_tencent
from helper_function.apis_requests import get_current_user
from datetime import datetime

async def create_slider(
    token: str = Depends(get_current_user),
    name: str = Form(...),
    type: str = Form(...),  # course, redirection, promotional
    visible: bool = Form(...),
    course_id: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(default=None)
):
    """Create slider with type options: course, redirection, promotional"""
    try:
        # Check if slider with same name already exists
        existing_slider = await sliders_collection.find_one({"name": name})
        if existing_slider:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Slider with this name already exists"
                }
            )
        
        # Validate type
        valid_types = ["course", "redirection", "promotional"]
        if type not in valid_types:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "type must be course, redirection, or promotional"
                }
            )
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Type-specific validation and data preparation
        slider_data = {
            "name": name,
            "type": type,
            "visible": visible,
            "created_at": current_time
        }
        
        if type == "course":
            if not course_id:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "course_id is required for course type"
                    }
                )
            if not ObjectId.is_valid(course_id):
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "Invalid course_id format"
                    }
                )
            
            # Verify course exists
            course = await courses_collection.find_one({"_id": ObjectId(course_id)})
            if not course:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": 404,
                        "message": "Course not found"
                    }
                )
            
            slider_data["course_id"] = ObjectId(course_id)
            # slider_data["image_url"] = course.get("images", {}).get("course_image_url", "")
            
        elif type == "redirection":
            if not url:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "url is required for redirection type"
                    }
                )
            slider_data["url"] = url
            
            # Handle optional image with proper FileId
            if image and image.filename:
                image_content = await image.read()
                image_result = await upload_image_to_tencent(image_content, image.filename)
                slider_data["image"] = {
                    "fileId": image_result["file_id"],
                    "image_url": image_result["image_url"],
                    "uploaded_at": current_time
                }
                
        elif type == "promotional":
            # Both image and url are optional for promotional
            if image and image.filename:
                image_content = await image.read()
                image_result = await upload_image_to_tencent(image_content, image.filename)
                slider_data["image"] = {
                    "fileId": image_result["file_id"],
                    "image_url": image_result["image_url"],
                    "uploaded_at": current_time
                }
            
            if url:
                slider_data["url"] = url
        
        # Insert slider
        result = await sliders_collection.insert_one(slider_data)
        
        # Prepare response (excluding fileId and created_at)
        response_data = {
            "_id": str(result.inserted_id),
            "name": name,
            "type": type,
            "visible": visible
        }
        
        # Add type-specific fields to response
        if type == "course":
            response_data["course_id"] = course_id
        elif type == "redirection":
            response_data["url"] = url
            if "image" in slider_data:
                response_data["image_url"] = slider_data["image"]["image_url"]
        elif type == "promotional":
            if "url" in slider_data:
                response_data["url"] = url
            if "image" in slider_data:
                response_data["image_url"] = slider_data["image"]["image_url"]
        
        return {
            "status": 201,
            "message": "Slider created successfully",
            "data": response_data
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": f"Failed to create slider: {str(e)}"
            }
        )