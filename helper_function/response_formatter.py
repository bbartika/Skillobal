from fastapi.responses import JSONResponse
from typing import Any, Optional

class StandardResponse:
    """Standardized response formatter for consistent API responses"""
    
    @staticmethod
    def success(
        message: str = "Operation successful",
        data: Any = None,
        status_code: int = 200
    ) -> JSONResponse:
        """Standard success response format"""
        response_body = {
            "success": True,
            "message": message,
            "status_code": status_code
        }
        if data is not None:
            response_body["data"] = data
            
        return JSONResponse(content=response_body, status_code=status_code)
    
    @staticmethod
    def error(
        message: str = "Operation failed",
        error_details: Optional[str] = None,
        status_code: int = 400
    ) -> JSONResponse:
        """Standard error response format"""
        response_body = {
            "success": False,
            "message": message,
            "status_code": status_code
        }
        if error_details:
            response_body["error_details"] = error_details
            
        return JSONResponse(content=response_body, status_code=status_code)
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        field_errors: Optional[dict] = None,
        status_code: int = 422
    ) -> JSONResponse:
        """Standard validation error response format"""
        response_body = {
            "success": False,
            "message": message,
            "status_code": status_code
        }
        if field_errors:
            response_body["field_errors"] = field_errors
            
        return JSONResponse(content=response_body, status_code=status_code)
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_details: Optional[str] = None,
        status_code: int = 500
    ) -> JSONResponse:
        """Standard server error response format"""
        response_body = {
            "success": False,
            "message": message,
            "status_code": status_code
        }
        if error_details:
            response_body["error_details"] = error_details
            
        return JSONResponse(content=response_body, status_code=status_code)