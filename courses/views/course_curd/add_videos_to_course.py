from fastapi import HTTPException, Request, Form, File, UploadFile, Depends
from typing import List, Optional
from bson import ObjectId
from core.database import courses_collection, courses_videos_collection
from helper_function.video_upload import upload_to_tencent_vod
from helper_function.apis_requests import get_current_user
from datetime import datetime

async def add_videos_to_course(
    course_id: str,
    request: Request,
    token: str = Depends(get_current_user),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    order: Optional[str] = Form(None),
    video_file: List[UploadFile] = File([]),
    assignment: Optional[str] = Form(None),  # Comma-separated video indexes: "2,4" means add assignment after 2nd and 4th video
):
    """Add videos and assignments to existing course"""
    try:
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        video_ids = []
        
        # Upload videos
        if video_file and len(video_file) > 0 and video_file[0].filename:
            titles = video_title.split(',') if video_title else []
            descriptions = video_description.split(',') if video_description else []
            orders = order.split(',') if order else []
            
            for i, vid_file in enumerate(video_file):
                if vid_file.filename:
                    video_content = await vid_file.read()
                    video_result = await upload_to_tencent_vod(video_content, vid_file.filename)
                    
                    base_order = int(orders[i].strip()) if i < len(orders) and orders[i].strip().isdigit() else (i + 1) * 2
                    
                    video_obj = {
                        "order": base_order,
                        "video_title": titles[i].strip() if i < len(titles) else f"Video {i+1}",
                        "video_description": descriptions[i].strip() if i < len(descriptions) else "",
                        "fileId": video_result["file_id"],
                        "videoUrl": video_result["video_url"],
                        "type": "video",
                        "course_id": course_id,
                        "created_at": current_time
                    }
                    
                    video_doc_result = await courses_videos_collection.insert_one(video_obj)
                    video_ids.append(video_doc_result.inserted_id)
        
        # Get current videos array
        current_videos = course.get("videos", [])
        
        # Add new video IDs
        current_videos.extend(video_ids)
        
        # Parse assignment indexes (1-based indexing from user input)
        assignment_video_indexes = []
        if assignment:
            try:
                assignment_video_indexes = [int(idx.strip()) for idx in assignment.split(',') if idx.strip().isdigit()]
            except:
                pass
        
        # Build final videos array with assignments inserted after specified video indexes
        final_videos = []
        video_count = 0
        
        for item in current_videos:
            if isinstance(item, ObjectId):
                video_count += 1
                final_videos.append(item)
                # Check if assignment should be added after this video
                if video_count in assignment_video_indexes:
                    final_videos.append("assignment")
            else:
                final_videos.append(item)
        
        # Update course with new videos array
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": {"videos": final_videos}}
        )
        
        return {
            "success": True,
            "message": f"Added {len(video_ids)} videos and {len(assignment_video_indexes)} assignments to course",
            "video_ids": [str(vid) for vid in video_ids],
            "assignments_added_after_video_indexes": assignment_video_indexes,
            "total_items_in_course": len(final_videos)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
