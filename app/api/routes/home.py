from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/api/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    return templates.TemplateResponse(
        request,                 #  REQUIRED para esta versión
        "index.html",             # nombre del template
        {"request": request}      # contexto
    )