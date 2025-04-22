import datetime

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import members_collection, feedback_collection
from models import Member, Feedback
from bson.objectid import ObjectId

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register")
def register(name: str = Form(...), member_id: str = Form(...)):
    if not members_collection.find_one({"member_id": member_id}):
        members_collection.insert_one({"name": name, "member_id": member_id})
    return RedirectResponse(url=f"/feedback/{member_id}", status_code=303)


@app.get("/feedback/{member_id}")
def feedback_form(request: Request, member_id: str):
    member = members_collection.find_one({"member_id": member_id})
    return templates.TemplateResponse("feedback.html", {"request": request, "member": member})


@app.post("/submit_feedback/{member_id}")
def submit_feedback(
        member_id: str,
        farmer_name: str = Form(...),
        address: str = Form(...),
        mobile: str = Form(...),
        total_land: str = Form(...),
        used_area: str = Form(...),
        crops: str = Form(...),
        products_used: str = Form(...),
        feedback: str = Form(...),
        date: str = Form(...)
):
    feedback_data = Feedback(
        member_id=member_id,
        farmer_name=farmer_name,
        address=address,
        mobile=mobile,
        total_land=total_land,
        used_area=used_area,
        crops=crops,
        products_used=products_used,
        feedback=feedback,
        date=date,
        created_at=datetime.datetime.now()
    )
    try:
        # Insert the feedback into MongoDB
        feedback_collection.insert_one(feedback_data.dict())
        return RedirectResponse(
            url=f"/feedback/{member_id}?success=true",
            status_code=303
        )

    # except PyMongoError as e:  # Catch MongoDB-related exceptions
    #     print(f"Database error: {e}")
    #     return RedirectResponse(
    #         url=f"/feedback/{member_id}?error=db_error",
    #         status_code=303
    #     )
    except Exception as e:  # Catch other generic errors
        print(f"Unexpected error: {e}")
        return RedirectResponse(
            url=f"/feedback/{member_id}?error=unknown_error",
            status_code=303
        )



# Hardcoded admin credentials
ADMIN_USERNAME = "ecoadmin"
ADMIN_PASSWORD = "eco@save25"

# Middleware for fake session (simple example)
admin_sessions = {}

@app.get("/admin", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        admin_sessions["logged_in"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if not admin_sessions.get("logged_in"):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/admin/logout")
def admin_logout():
    admin_sessions.clear()
    return RedirectResponse(url="/admin", status_code=302)


@app.get("/admin/feedbacks", response_class=HTMLResponse)
def view_feedbacks(request: Request):
    if not admin_sessions.get("logged_in"):
        return RedirectResponse(url="/admin", status_code=302)

    feedbacks = list(feedback_collection.find())
    member_ids = {fb['member_id'] for fb in feedbacks}
    members = {
        m['member_id']: m['name'] for m in members_collection.find({"member_id": {"$in": list(member_ids)}})
    }

    # Attach member names to feedbacks
    for fb in feedbacks:
        fb['member_name'] = members.get(fb['member_id'], "Unknown")

    return templates.TemplateResponse("view_feedbacks.html", {
        "request": request,
        "feedbacks": feedbacks
    })
