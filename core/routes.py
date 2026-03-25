from fastapi import APIRouter
from user.userRoutes import user_router
from courses.coursesRoutes import courses_router
from sliders.sliderRoutes import slider_router
from ai_features.aiFeatureRoutes import aiFeatureRoutes
from dashboard.dashboardRoutes import dashboard_router
from languages.languagesRoutes import router as languages_router
from categories.categoriesRoutes import router as categories_router
from instructors.instructorsRoutes import router as instructors_router
from layout import layout_router

api_router = APIRouter()

# Include all module routers
api_router.include_router(user_router)
api_router.include_router(courses_router)
api_router.include_router(slider_router)
api_router.include_router(aiFeatureRoutes)
api_router.include_router(dashboard_router)
api_router.include_router(languages_router)
api_router.include_router(categories_router)
api_router.include_router(instructors_router)
api_router.include_router(layout_router)


