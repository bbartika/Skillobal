from fastapi import Request, Body, HTTPException, Depends, Form, File, UploadFile
from typing import Optional, List
from bson import ObjectId
from core.database import courses_collection, courses_videos_collection, course_intro_video_collection
from helper_function.video_upload import upload_to_tencent_vod
from helper_function.image_upload import upload_image_to_tencent
from helper_function.apis_requests import get_current_user
from datetime import datetime

async def create_course(
    request: Request,
    token: str = Depends(get_current_user),
    title: str = Form(...),
    description: str = Form(...),
    category_id: str = Form(...),
    language_id: str = Form(...),
    visible: bool = Form(...),
    skills: Optional[str] = Form(None),
    course_image_url: Optional[UploadFile] = File(None),
    course_intro_video: Optional[UploadFile] = File(None),
    rating: Optional[int] = Form(None),
    price: Optional[str] = Form(None),
    instructor_id: Optional[str] = Form(None),
    layout_id: str = Form(...),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    order: Optional[str] = Form(None),
    video_file: List[UploadFile] = File([]),
):
    """Create course with optional video upload"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create individual video documents
        video_ids = []
        
        # Handle video files
        if video_file and len(video_file) > 0 and video_file[0].filename:
            titles = video_title.split(',') if video_title else []
            descriptions = video_description.split(',') if video_description else []
            orders = order.split(',') if order else []
            
            for i, vid_file in enumerate(video_file):
                if vid_file.filename:
                    video_content = await vid_file.read()
                    video_result = await upload_to_tencent_vod(video_content, vid_file.filename)
                    
                    base_order = int(orders[i].strip()) if i < len(orders) and orders[i].strip().isdigit() else (i + 1) * 2
                    
                    # Create video document
                    video_obj = {
                        "order": base_order,
                        "video_title": titles[i].strip() if i < len(titles) else f"Video {i+1}",
                        "video_description": descriptions[i].strip() if i < len(descriptions) else "",
                        "fileId": video_result["file_id"],
                        "videoUrl": video_result["video_url"],
                        "type": "video",
                        "created_at": current_time
                    }
                    
                    video_doc_result = await courses_videos_collection.insert_one(video_obj)
                    video_ids.append(video_doc_result.inserted_id)

        # Handle course image upload
        image_obj = None
        
        if course_image_url and course_image_url.filename:
            course_image_content = await course_image_url.read()
            course_image_result = await upload_image_to_tencent(course_image_content, course_image_url.filename)
            
            image_obj = {
                "fileId": course_image_result["file_id"],
                "course_image_url": course_image_result["image_url"],
                # "type": "course_image",
            }
        
        # Handle course intro video upload
        intro_video_obj = None
        
        if course_intro_video and course_intro_video.filename:
            course_intro_video_content = await course_intro_video.read()
            course_intro_video_result = await upload_to_tencent_vod(course_intro_video_content, course_intro_video.filename)
            
            intro_video_obj = {
                "fileId": course_intro_video_result["file_id"],
                "videoUrl": course_intro_video_result["video_url"],
                # "type": "intro_video",
            }
            
        # Parse comma-separated IDs into arrays
        category_id_list = [ObjectId(id.strip()) for id in category_id.split(',') if id.strip() and id.strip() != "string"]
        language_id_list = [ObjectId(id.strip()) for id in language_id.split(',') if id.strip() and id.strip() != "string"]
        instructor_id_list = [ObjectId(id.strip()) for id in instructor_id.split(',') if instructor_id and id.strip() and id.strip() != "string"] if instructor_id else []
        layout_id_list = [ObjectId(id.strip()) for id in layout_id.split(',') if id.strip() and id.strip() != "string"]
        
        # Parse comma-separated skills into array
        skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()] if skills else []

        # Create videos array with assignment strings for videos that have assignments
        # NOTE: This code is commented out because assignments are handled via add_video_to_course API
        # videos_array = []
        # for video_id in video_ids:
        #     video = await courses_videos_collection.find_one({"_id": video_id})
        #     if video and "ai_generated_content" in video and "assignment" in video["ai_generated_content"]:
        #         videos_array.append("assignment")
        #     else:
        #         videos_array.append(video_id)
        videos_array = video_ids
        
        new_course = {
            "title": title,
            "description": description,
            "category_id": category_id_list,
            "language_id": language_id_list,
            "visible": visible,
            "skills": skills_list,
            "images": image_obj,
            "intro_videos": intro_video_obj,
            "videos": videos_array,
            "rating": rating,
            "price": round(float(price), 2) if price else 0.0,
            "instructor_id": instructor_id_list,
            "layout_id": layout_id_list,
            "created_at": current_time
        }

        result = await courses_collection.insert_one(new_course)
        course_id = str(result.inserted_id)
        
        # Update all videos with course_id
        if video_ids:
            await courses_videos_collection.update_many(
                {"_id": {"$in": video_ids}},
                {"$set": {"course_id": course_id}}
            )
        
        new_course["_id"] = course_id
        new_course["instructor_id"] = [str(id) for id in new_course["instructor_id"]]
        new_course["category_id"] = [str(id) for id in new_course["category_id"]]
        new_course["language_id"] = [str(id) for id in new_course["language_id"]]
        new_course["layout_id"] = [str(id) for id in new_course["layout_id"]]

        if new_course["videos"]:
            new_course["videos"] = [str(vid_id) for vid_id in new_course["videos"]]

        # Fetch videos data for response sorted by order
        videos_data = []
        if video_ids:
            videos_cursor = courses_videos_collection.find({"_id": {"$in": video_ids}}).sort("order", 1)
            async for video in videos_cursor:
                video["_id"] = str(video["_id"])
                if "parent_video_id" in video:
                    video["parent_video_id"] = str(video["parent_video_id"])
                # Keep type field for frontend to distinguish
                video.pop("created_at", None)
                videos_data.append(video)
        
        # Format response for frontend compatibility
        response_data = {
            "_id": course_id,
            "title": title,
            "description": description,
            "images": image_obj,
            "intro_videos": intro_video_obj,
            "rating": rating or 0,
            "price": round(float(price), 2) if price else 0.0,
            "visible": visible,
            "skills": skills_list,
            "instructor_id": new_course["instructor_id"],
            "category_id": new_course["category_id"],
            "language_id": new_course["language_id"],
            "layout_id": new_course["layout_id"],
            "videos": videos_data,  # Actual videos data
            "created_at": current_time
        }
        
        return {
            "success": True,
            "message": "Course created successfully",
            "data": response_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong while creating course")

