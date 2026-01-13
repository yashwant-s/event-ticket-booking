from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.exceptions import ApiBaseException
from app.schemas.response import ApiErrorResponse
from app.controllers.v1 import events, tickets
app = FastAPI()



@app.get("/health")
def health():
    return {"success": "true"}


@app.exception_handler(ApiBaseException)
async def api_exception_handler(request: Request, exc: ApiBaseException):

    error_response = ApiErrorResponse(
        success=False,
        message=exc.message,
        details=exc.details
    )

    return JSONResponse(
        status_code = exc.status_code,
        content = error_response.model_dump()
    )
    
app.include_router(events.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")


