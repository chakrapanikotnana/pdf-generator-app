import pandas as pd
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from app.validator import validate_excel
import tempfile
import os
from app.pdf_service import generate_pdfs
from fastapi.responses import PlainTextResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import validate_user, is_logged_in

app = FastAPI()

# Session middleware (required for login)
app.add_middleware(SessionMiddleware, secret_key="demo-secret-key")

# Templates
import os
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Static files for CSS and images
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# -----------------------
# Login Page
# -----------------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

# -----------------------
# Login Submit
# -----------------------
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    
    if validate_user(username, password):
        request.session["user"] = username
        return RedirectResponse("/upload", status_code=303)
    
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Invalid credentials"}
    )


# -----------------------
# Upload Page
# -----------------------
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    
    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(request, "upload.html")


# -----------------------
# Logout 
# -----------------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

# -----------------------
# Post Upload - Validate Excel
# -----------------------
@app.post("/upload")
async def upload_excel(request: Request, file: UploadFile = File(...)):

    if not is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    try:
        file.file.seek(0)
        df = pd.read_excel(file.file)

        errors = validate_excel(df)

        if errors:
            return templates.TemplateResponse(
                request,
                "upload.html",
                {"errors": errors}
            )

        zip_path = generate_pdfs(df)

        return FileResponse(
            path=zip_path,
            filename="output.zip",
            media_type="application/zip"
        )

    except Exception as e:
        import traceback
        return templates.TemplateResponse(
            request,
            "upload.html",
            {"errors": [traceback.format_exc()]}
        )
