from fastapi import HTTPException, Depends
from bson import ObjectId
from core.database import courses_collection, courses_videos_collection, db
from helper_function.apis_requests import get_current_user
from helper_function.validate_references import validate_course_references

layout_collection = db['layout']

def convert_objectids(obj):
    """Recursively convert ObjectIds to strings"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectids(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(item) for item in obj]
    else:
        return obj

async def get_specific_course_details(
    course_id: str,
    token: str = Depends(get_current_user)
):
    """Get complete details of a specific course including all videos"""
    try:
        # Validate course_id
        if not ObjectId.is_valid(course_id):
            return {
                "success": False,
                "message": "Invalid course ID"
            }
        
        # Get course details
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            return {
                "success": False,
                "message": "Course not found"
            }
        
        # Validate and clean invalid references
        course = await validate_course_references(course)
        
        # Handle layout_id - filter out layouts with status=false
        if "layout_id" in course and course["layout_id"]:
            valid_layout_ids = []
            for layout_id in course["layout_id"]:
                layout = await layout_collection.find_one({"_id": layout_id, "status": True})
                if layout:
                    valid_layout_ids.append(layout_id)
            course["layout_id"] = valid_layout_ids
        else:
            course["layout_id"] = []
        
        # Fetch complete video details - handle mixed array
        if "videos" in course and course["videos"]:
            try:
                # Get video documents
                video_object_ids = [v for v in course["videos"] if isinstance(v, ObjectId)]
                videos_cursor = courses_videos_collection.find({"_id": {"$in": video_object_ids}}).sort("order", 1)
                video_docs = {str(v["_id"]): v async for v in videos_cursor}
                
                # Build videos_details in sequence and collect course-level data
                videos_details = []
                first_video_questions = 0
                course_hinglish = False
                
                for item in course["videos"]:
                    if isinstance(item, ObjectId):
                        video = video_docs.get(str(item))
                        if video:
                            # Count AI generated questions
                            ai_content = video.get("ai_generated_content", {})
                            individual_questions = ai_content.get("individual_questions", {})
                            
                            question_count = 0
                            for category in ["easy_difficult_questions", "medium_difficult_questions", "hard_difficult_questions"]:
                                if category in individual_questions:
                                    question_count += len(individual_questions[category])
                            
                            # Only take first video's question count
                            if first_video_questions == 0:
                                first_video_questions = question_count
                                
                            if ai_content.get("hinglish", False):
                                course_hinglish = True
                            
                            # Remove unwanted fields
                            video.pop("_id", None)
                            video.pop("type", None)
                            video.pop("created_at", None)
                            video.pop("ai_generated_content", None)
                            video.pop("course_id", None)
                            videos_details.append(video)
                    elif item == "assignment":
                        videos_details.append("assignment")
                
                course["videos_details"] = videos_details
                course["number_of_question"] = first_video_questions
                course["hinglish"] = course_hinglish
                
            except Exception as e:
                course["videos_details"] = []
                course["number_of_question"] = 0
                course["hinglish"] = False
        else:
            course["videos_details"] = []
            course["number_of_question"] = 0
            course["hinglish"] = False
 
        # Remove videos array (keep only videos_details)
        if "videos" in course:
            del course["videos"]
        
        # Clean intro_videos and images - remove type and uploaded_at
        if "intro_videos" in course and course["intro_videos"]:
            course["intro_videos"].pop("type", None)
            course["intro_videos"].pop("uploaded_at", None)
        
        if "images" in course and course["images"]:
            course["images"].pop("type", None)
            course["images"].pop("uploaded_at", None)
        
        # Ensure skills field is included
        if "skills" not in course:
            course["skills"] = []
        
        # Build response in required format
        response_data = {
            "id": str(course["_id"]),
            "title": course.get("title", ""),
            "description": course.get("description", ""),
            "category_id": [str(id) for id in course.get("category_id", [])],
            "language_id": [str(id) for id in course.get("language_id", [])],
            "visible": course.get("visible", False),
            "skills": course.get("skills", []),
            "course_image_url": course.get("images", {}).get("course_image_url", "") if course.get("images") else "",
            "videoUrl": course.get("intro_videos", {}).get("videoUrl", "") if course.get("intro_videos") else "",
            "rating": course.get("rating", 0),
            "price": course.get("price", 0),
            "instructor_id": [str(id) for id in course.get("instructor_id", [])],
            "layout_id": [str(id) for id in course.get("layout_id", [])],
            "videos_details": course.get("videos_details", []),
            "number_of_question": course.get("number_of_question", 0),
            "hinglish": course.get("hinglish", False)
        }
        
        return {
            "success": True,
            "message": "Course details fetched successfully",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": "Something went wrong while fetching course details"
        }