from fastapi import APIRouter
from sliders.views.create_slider import create_slider
from sliders.views.get_sliders import get_all_sliders
from sliders.views.update_slider import update_slider
from sliders.views.delete_slider import delete_slider


slider_router = APIRouter(prefix="/admin/sliders", tags=["Sliders"])

# Create slider
slider_router.add_api_route(
    "/create",
    create_slider,
    methods=["POST"],
    tags=["Sliders"],
    summary="Create new slider"
)

# Get all sliders (admin)
slider_router.add_api_route(
    "",
    get_all_sliders,
    methods=["GET"],
    tags=["Sliders"],
    summary="Get all sliders"
)



# Update slider
slider_router.add_api_route(
    "/update/{slider_id}",
    update_slider,
    methods=["PUT"],
    tags=["Sliders"],
    summary="Update slider"
)

# Delete slider
slider_router.add_api_route(
    "/delete/{slider_id}",
    delete_slider,
    methods=["DELETE"],
    tags=["Sliders"],
    summary="Delete slider"
)

