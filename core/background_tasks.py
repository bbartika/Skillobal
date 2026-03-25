from fastapi import BackgroundTasks
from typing import Callable, Any
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manage background tasks efficiently"""
    
    @staticmethod
    async def cleanup_old_files(file_ids: list):
        """Delete old files from Tencent in background"""
        from helper_function.video_upload import delete_from_tencent_vod
        
        for file_id in file_ids:
            try:
                await delete_from_tencent_vod(file_id)
                logger.info(f"Deleted file: {file_id}")
            except Exception as e:
                logger.error(f"Failed to delete {file_id}: {e}")
    
    @staticmethod
    async def update_course_statistics(course_id: str):
        """Update course statistics in background"""
        from core.database import courses_collection, courses_videos_collection
        from bson import ObjectId
        
        try:
            # Count total videos
            video_count = await courses_videos_collection.count_documents({
                "course_id": course_id
            })
            
            # Update course
            await courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": {
                    "total_videos": video_count,
                    "stats_updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }}
            )
            logger.info(f"Updated stats for course: {course_id}")
        except Exception as e:
            logger.error(f"Failed to update stats for {course_id}: {e}")
    
    @staticmethod
    async def send_notification(user_id: str, message: str):
        """Send notification in background"""
        # Implement notification logic here
        logger.info(f"Notification sent to {user_id}: {message}")
    
    @staticmethod
    async def log_activity(user_id: str, action: str, details: dict):
        """Log user activity in background"""
        from core.database import db
        
        try:
            activity_log = {
                "user_id": user_id,
                "action": action,
                "details": details,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            await db.activity_logs.insert_one(activity_log)
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

def add_background_task(background_tasks: BackgroundTasks, func: Callable, *args, **kwargs):
    """Helper to add background tasks"""
    background_tasks.add_task(func, *args, **kwargs)
