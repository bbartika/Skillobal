from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from bson import ObjectId
from core.database import db, courses_collection, sliders_collection
from helper_function.apis_requests import get_current_user


async def get_all_sliders(
    token: str = Depends(get_current_user),
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    """Get all sliders with populated course data"""
    try:
        skip = (page - 1) * limit
        
        # Get total count
        total_sliders = await sliders_collection.count_documents({})
        
        # Get paginated sliders
        sliders = await sliders_collection.find().skip(skip).limit(limit).to_list(None)
        
        result_sliders = []
        for slider in sliders:
            slider_data = {
                "_id": str(slider["_id"]),
                "name": slider.get("name", slider.get("slide_name", "")),
                "type": slider.get("type", slider.get("slider_type", "")),
                "visible": slider["visible"]
            }
            
            # Get slider type (backward compatibility)
            slider_type = slider.get("type", slider.get("slider_type", ""))
            
            # Add type-specific data
            if (slider_type == "course" or slider_type == "course_id") and "course_id" in slider:
                course = await courses_collection.find_one({"_id": slider["course_id"]})
                slider_data["course_id"] = str(slider["course_id"])
                slider_data["image_url"] = slider.get("image_url", slider.get("course_image_url", ""))
                slider_data["course_data"] = {
                    "title": course["title"] if course else "Course not found",
                    "description": course.get("description", "") if course else ""
                } if course else None
                
            elif slider_type in ["redirection", "promotional", "redirection_link"]:
                if "url" in slider:
                    slider_data["url"] = slider["url"]
                if "image" in slider:
                    slider_data["image_url"] = slider["image"]["image_url"]
                    slider_data["fileId"] = slider["image"]["fileId"]
            
            result_sliders.append(slider_data)
        
        total_pages = (total_sliders + limit - 1) // limit
        
        return {
            "status": 200,
            "message": "Sliders retrieved successfully",
            "data": result_sliders,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_sliders": total_sliders,
                "limit": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": f"Failed to retrieve sliders: {str(e)}"
            }
        )

async def get_visible_sliders(token: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Get only visible sliders for public display"""
    try:
        sliders = await sliders_collection.find({"visible": True}).to_list(None)
        
        result_sliders = []
        for slider in sliders:
            slider_data = {
                "_id": str(slider["_id"]),
                "name": slider.get("name", slider.get("slide_name", "")),
                "type": slider.get("type", slider.get("slider_type", ""))
            }
            
            # Get slider type (backward compatibility)
            slider_type = slider.get("type", slider.get("slider_type", ""))
            
            # Add type-specific data
            if (slider_type == "course" or slider_type == "course_id") and "course_id" in slider:
                course = await courses_collection.find_one({"_id": slider["course_id"]})
                slider_data["image_url"] = slider.get("image_url", slider.get("course_image_url", ""))
                if course:
                    slider_data["course_data"] = {
                        "title": course["title"],
                        "description": course.get("description", ""),
                        "course_id": str(course["_id"])
                    }
                    
            elif slider_type in ["redirection", "promotional", "redirection_link"]:
                if "url" in slider:
                    slider_data["url"] = slider["url"]
                if "image" in slider:
                    slider_data["image_url"] = slider["image"]["image_url"]
            
            result_sliders.append(slider_data)
        
        return {
            "status": 200,
            "message": "Visible sliders retrieved successfully",
            "data": result_sliders,
            "total": len(result_sliders)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": f"Failed to retrieve visible sliders: {str(e)}"
            }
        )