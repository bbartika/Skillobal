from fastapi import HTTPException, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from core.database import db, courses_collection, sliders_collection
from helper_function.image_upload import upload_image_to_tencent
from helper_function.video_upload import delete_from_tencent_vod
from helper_function.apis_requests import get_current_user
from datetime import datetime


async def update_slider(
    slider_id: str,
    token: str = Depends(get_current_user),
    name: Optional[str] = Form(None),
    type: Optional[str] = Form(None),  # course, redirection, promotional
    visible: Optional[bool] = Form(None),
    course_id: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(default=None)
):
    """Update slider with type validation"""
    try:
        if not ObjectId.is_valid(slider_id):
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Invalid slider ID"
                }
            )
        
        # Get existing slider
        existing_slider = await sliders_collection.find_one({"_id": ObjectId(slider_id)})
        if not existing_slider:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "message": "Slider not found"
                }
            )
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_data = {"updated_at": current_time}
        old_file_id = None
        
        # Check if at least one field is provided
        fields = [name, type, visible, course_id, url]
        if not any(field is not None for field in fields) and not (image and image.filename):
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "At least one field must be provided for update"
                }
            )
        
        # Update basic fields
        if name is not None:
            update_data["name"] = name
        if visible is not None:
            update_data["visible"] = visible
        
        # Handle type change
        current_type = existing_slider.get("type", existing_slider.get("slider_type", ""))
        new_type = type if type is not None else current_type
        
        if type is not None:
            valid_types = ["course", "redirection", "promotional"]
            if new_type not in valid_types:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "type must be course, redirection, or promotional"
                    }
                )
            update_data["type"] = new_type
            
            # Delete old image when type changes
            if current_type != new_type and "image" in existing_slider and existing_slider["image"].get("fileId"):
                old_file_id = existing_slider["image"]["fileId"]
        
        # Type-specific validation and updates
        if new_type == "course":
            if course_id is not None:
                if not ObjectId.is_valid(course_id):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "status": 400,
                            "message": "Invalid course_id format"
                        }
                    )
                
                course = await courses_collection.find_one({"_id": ObjectId(course_id)})
                if not course:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": 404,
                            "message": "Course not found"
                        }
                    )
                
                update_data["course_id"] = ObjectId(course_id)
                update_data["course_image_url"] = course.get("images", {}).get("course_image_url", "")
            elif "course_id" not in existing_slider:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "course_id is required for course type"
                    }
                )
            
            # Remove url and image fields if changing to course type
            if current_type != "course":
                update_data["$unset"] = {"url": "", "image": ""}
                    
        elif new_type == "redirection":
            if url is not None:
                update_data["url"] = url
            elif "url" not in existing_slider:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": 400,
                        "message": "url is required for redirection type"
                    }
                )
            
            # Remove course_id if changing from course type
            if current_type == "course":
                if "$unset" not in update_data:
                    update_data["$unset"] = {}
                update_data["$unset"]["course_id"] = ""
            
            # Handle image update
            if image and image.filename:
                if "image" in existing_slider and existing_slider["image"].get("fileId"):
                    old_file_id = existing_slider["image"]["fileId"]
                
                image_content = await image.read()
                image_result = await upload_image_to_tencent(image_content, image.filename)
                update_data["image"] = {
                    "fileId": image_result["file_id"],
                    "image_url": image_result["image_url"],
                    "uploaded_at": current_time
                }
                
        elif new_type == "promotional":
            # Remove course_id if changing from course type
            if current_type == "course":
                if "$unset" not in update_data:
                    update_data["$unset"] = {}
                update_data["$unset"]["course_id"] = ""
            
            # Update url if provided
            if url is not None:
                update_data["url"] = url
            
            # Handle image update
            if image and image.filename:
                if "image" in existing_slider and existing_slider["image"].get("fileId"):
                    old_file_id = existing_slider["image"]["fileId"]
                
                image_content = await image.read()
                image_result = await upload_image_to_tencent(image_content, image.filename)
                update_data["image"] = {
                    "fileId": image_result["file_id"],
                    "image_url": image_result["image_url"],
                    "uploaded_at": current_time
                }
        
        # Perform update
        if "$unset" in update_data:
            unset_data = update_data.pop("$unset")
            await sliders_collection.update_one(
                {"_id": ObjectId(slider_id)},
                {"$set": update_data, "$unset": unset_data}
            )
        else:
            await sliders_collection.update_one(
                {"_id": ObjectId(slider_id)},
                {"$set": update_data}
            )
        
        # Delete old image file if replaced
        if old_file_id:
            try:
                await delete_from_tencent_vod(old_file_id)
            except Exception:
                pass  # Don't fail update if cleanup fails
        
        # Prepare response with only updated values
        response_data = {}
        
        if name is not None and existing_slider.get("name") != name:
            response_data["name"] = name
        if type is not None and current_type != new_type:
            response_data["type"] = new_type
        if visible is not None and existing_slider.get("visible") != visible:
            response_data["visible"] = visible
        if course_id is not None and str(existing_slider.get("course_id", "")) != course_id:
            response_data["course_id"] = course_id
        if url is not None and existing_slider.get("url") != url:
            response_data["url"] = url
        if image and image.filename:
            new_image_url = update_data.get("image", {}).get("image_url")
            response_data["image_url"] = new_image_url
        
        # Check if no changes were made
        if not response_data:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "No changes detected. At least one field must be different to update."
                }
            )
        
        return {
            "status": 200,
            "message": "Slider updated successfully",
            "data": response_data
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": f"Failed to update slider: {str(e)}"
            }
        )