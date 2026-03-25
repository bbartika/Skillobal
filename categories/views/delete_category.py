from fastapi import HTTPException, Request, Depends
from bson import ObjectId
from core.database import categories_collection, courses_collection
from helper_function.video_upload import delete_from_tencent_vod
from helper_function.apis_requests import get_current_user

async def delete_category(
    category_id: str,
    request: Request,
    token: str = Depends(get_current_user)
):
    """Delete category and its image from Tencent Cloud"""
    try:
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail={"message": "Invalid category ID format. Please provide a valid category identifier."})
        
        # Check if category exists
        category = await categories_collection.find_one({"_id": ObjectId(category_id)})
        if not category:
            raise HTTPException(status_code=404, detail={"message": "Category not found. Please verify the category ID and try again."})
        
        # Remove category from all courses (cascade update)
        await courses_collection.update_many(
            {"category_id": ObjectId(category_id)},
            {"$pull": {"category_id": ObjectId(category_id)}}
        )
        
        # Delete image from Tencent Cloud
        if "image" in category and category["image"] and category["image"].get("fileId"):
            try:
                await delete_from_tencent_vod(category["image"]["fileId"])
            except Exception:
                pass
        
        # Delete category from database
        await categories_collection.delete_one({"_id": ObjectId(category_id)})
        
        return {
            "success": True,
            "message": "Category deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Failed to delete category. Please try again later."})