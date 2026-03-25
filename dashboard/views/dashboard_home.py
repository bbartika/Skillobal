from fastapi import HTTPException, Depends, Request
from user.views.list_users import list_users
from core.database import courses_collection, sliders_collection, db

from helper_function.apis_requests import get_current_user

layout_collection = db['layout']

async def get_dashboard_home(
    request: Request,
    token: str = Depends(get_current_user)
):
    """Get dashboard home data with statistics"""
    try:
        # Get user data (reuse existing logic)
        user_data = await list_users(request=request, token=token)
        
        # Get total courses count
        total_courses = await courses_collection.count_documents({})
        
        # Get visible courses count
        visible_courses = await courses_collection.count_documents({"visible": True})
        
        # Get visible sliders count
        visible_sliders = await sliders_collection.count_documents({"visible": True})
        
        # Get layout data with course details
        layouts = await layout_collection.find({"status": True}).to_list(length=None)
        section_layout = []
        
        for layout in layouts:
            # Find courses that have this layout_id
            courses_with_layout = await courses_collection.find(
                {"layout_id": layout["_id"], "visible": True}
            ).to_list(length=None)
            
            courses_data = [
                {
                    "id": str(course["_id"]),
                    "name": course.get("title", ""),
                    "course_image_url": course.get("images", {}).get("course_image_url", ""),
                    "rating": course.get("rating", 0),
                    "price": course.get("price", 0),
                    "enrolled": course.get("enrolled", 0)
                }
                for course in courses_with_layout
            ]
            
            if layout.get("status", True):  # Only add if visible is true
                section_layout.append({
                    "title": layout.get("title", ""),
                    "description": layout.get("description", ""),
                    "visible": layout.get("status", True),
                    "courses": courses_data
                })
        
        # Get latest 3 courses with visible=true
        top_courses_cursor = courses_collection.find({"visible": True}).sort("_id", -1).limit(3)
        top_courses_list = await top_courses_cursor.to_list(length=None)
        
        # Get visible sliders list
        # sliders_cursor = sliders_collection.find({"visible": True})
        # sliders_list = await sliders_cursor.to_list(length=None)
        
        top_courses_data = {
            "data": {
                "top_courses": [
                    {
                        "name": course.get("title", ""),
                        "course_image_url": course.get("images", {}).get("course_image_url", ""),
                        "rating": course.get("rating", 0),
                        "price": course.get("price", 0),
                        "enrolled": course.get("enrolled", 0)
                    }
                    for course in top_courses_list
                ]
            }
        }
        
        # Prepare dashboard statistics
        dashboard_stats = {
            "total_users": user_data.get("total", 0),
            "total_courses": total_courses,
            "visible_courses": visible_courses,
            "hidden_courses": total_courses - visible_courses,
            "total_sliders": visible_sliders,
            "total_revenue": 0,
            # "top_courses_count": len(top_courses_data["data"]["top_courses"])
        }
        
        # Prepare slider list
        # slider_list = []
        # for slider in sliders_list:
        #     slider_data = {
        #         "name": slider.get("name", ""),
        #         "type": slider.get("type", "")
        #     }
        #     
        #     if slider.get("type") == "course":
        #         slider_data["course_id"] = str(slider.get("course_id", ""))
        #     else:
        #         slider_data["image_url"] = slider.get("image", {}).get("image_url", "") if "image" in slider else ""
        #     
        #     slider_list.append(slider_data)
        
        return {
            "success": True,
            "message": "Dashboard data retrieved successfully",
            "data": {
                "statistics": dashboard_stats,
                "recent_users": user_data.get("users", [])[:5],  # Last 5 users
                "top_courses": top_courses_data["data"]["top_courses"][:5],  # Top 5 courses
                "section_layout": section_layout,
                # "slider_list": slider_list,
                "summary": {
                    "users": {
                        "total": dashboard_stats["total_users"],
                        "recent_count": len(user_data.get("users", [])[:5])
                    },
                    "courses": {
                        "total": dashboard_stats["total_courses"],
                        "visible": dashboard_stats["visible_courses"],
                        "hidden": dashboard_stats["hidden_courses"]
                    },
                    # "content": {
                    #     "top_courses": dashboard_stats["top_courses_count"]
                    # }
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")