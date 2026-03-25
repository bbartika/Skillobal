from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from core.database import sliders_collection
from helper_function.video_upload import delete_from_tencent_vod
from helper_function.apis_requests import get_current_user

async def delete_slider(
    slider_id: str,
    token: str = Depends(get_current_user)
):
    """Delete slider and its associated image from Tencent"""
    try:
        if not ObjectId.is_valid(slider_id):
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Invalid slider ID"
                }
            )
        
        # Get slider to check for image
        slider = await sliders_collection.find_one({"_id": ObjectId(slider_id)})
        if not slider:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "message": "Slider not found"
                }
            )
        
        # Delete image from Tencent if exists
        if "image" in slider and slider["image"].get("fileId"):
            try:
                await delete_from_tencent_vod(slider["image"]["fileId"])
            except Exception:
                pass  # Don't fail deletion if Tencent cleanup fails
        
        # Delete slider from database
        result = await sliders_collection.delete_one({"_id": ObjectId(slider_id)})
        
        return {
            "status": 200,
            "message": "Slider deleted successfully"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": f"Failed to delete slider: {str(e)}"
            }
        )