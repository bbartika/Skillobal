from fastapi import APIRouter
from layout.view.get import get_all_layouts
from layout.view.create import create_layout
from layout.view.update import update_layout
from layout.view.delete import delete_layout

layout_router = APIRouter(prefix="/admin/layout", tags=["Layout"])

# Layout CRUD operations
layout_router.add_api_route("/create", create_layout, methods=["POST"], description="Create new layout")
layout_router.add_api_route("/", get_all_layouts, methods=["GET"], description="Get all layouts")
layout_router.add_api_route("/{layout_id}/update", update_layout, methods=["PUT"], description="Update layout")
layout_router.add_api_route("/{layout_id}/delete", delete_layout, methods=["DELETE"], description="Delete layout")