import os

from fastapi import FastAPI, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.bookings.routes import router as bookings_router
from app.listings.routes import router as listings_router
from app.machines.routes import router as machines_router
from app.credentials.routes import router as credentials_router
from app.payments.routes import router as payments_router
from app.payments.webhooks import router as payments_webhooks_router
from app.disputes.routes import router as disputes_router
from app.organizations.routes import router as organizations_router
from app.providers.routes import router as providers_router
from app.compliance.routes import router as compliance_router
from app.invoices.routes import router as invoices_router
from app.benchmarks.routes import router as benchmarks_router
from app.metrics.routes import router as metrics_router


from app.auth.auth import optional_user


"""
This is the entrypoint of the FastAPI application.
It defines the API routes, page routes (templating with Jinja2), 
CORS configuration for cross origin requests, and cookie-based session handling.
"""

app = FastAPI(title="Remote Servers Marketplace", version="0.3")

FRONTEND_ORIGIN = "https://remote-servers-marketplace-test.onrender.com"

# Allow the browser frontend hosted on Render and local dev tools to call our API.
# Allow_credentials=True lets cookies and auth headers pass through.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(listings_router, prefix="/api/v1/listings", tags=["listings"])
app.include_router(bookings_router, prefix="/api/v1/bookings", tags=["bookings"])
app.include_router(machines_router, prefix="/api/v1/machines", tags=["machines"])
app.include_router(credentials_router, prefix="/api/v1/credentials", tags=["credentials"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(payments_webhooks_router, prefix="/api/v1/payments/webhooks", tags=["payments:webhooks"])
app.include_router(disputes_router, prefix="/api/v1/disputes", tags=["disputes"])
app.include_router(organizations_router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(providers_router, prefix="/api/v1/providers", tags=["providers"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(invoices_router, prefix="/api/v1/invoices", tags=["invoices"])
app.include_router(benchmarks_router, prefix="/api/v1/benchmarks", tags=["benchmarks"])
app.include_router(metrics_router, prefix="/api/v1/metrics", tags=["metrics"])


# App health endpoint
@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


# Define root paths for serving the frontend
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates_dir = os.path.join(BASE_DIR, "frontend", "templates")
static_dir = os.path.join(BASE_DIR, "frontend", "static")


# Serve lightweight HTML frontend directly using FastAPI and Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Define React build directory path
REACT_BUILD_DIR = os.path.join(BASE_DIR, "frontend", "static", "react")
react_build_exists = os.path.exists(REACT_BUILD_DIR)



# Define the StoreSession class to store sessions and cookies
class StoreSession(BaseModel):
    token: str


@app.post("/auth/store-session")
async def store_session(payload: StoreSession, response: Response):
    """Supabase gives us a JWT via the frontend.
    This endpoint stores it in an HttpOnly cookie so our 
    server-rendered HTML pages can know the logged-in user."""
    response.set_cookie(
        key="access_token",
        value=payload.token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
    )
    return {"status": "ok"}


# Pages (Jinja2 templating)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(optional_user)):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "user": user,
            "react_enabled": react_build_exists  # Pass this flag to template
        }
    )

# # Pages (Jinja2 templating)
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request, user=Depends(optional_user)):
#     return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(optional_user)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, user=Depends(optional_user)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/listings", response_class=HTMLResponse)
async def listings_page(request: Request, user=Depends(optional_user)):
    return templates.TemplateResponse("listings.html", {"request": request, "user": user})


@app.get("/bookings", response_class=HTMLResponse)
async def bookings_page(request: Request, user=Depends(optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("bookings.html", {"request": request, "user": user})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user=Depends(optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/payments/success", response_class=HTMLResponse)
async def payment_success_page(
    request: Request, 
    session_id: str = None, 
    booking_id: str = None,
    amount: float = None,
    currency: str = "USD",
    user=Depends(optional_user)
):
    return templates.TemplateResponse(
        "payment_success.html", 
        {
            "request": request, 
            "user": user,
            "session_id": session_id,
            "booking_id": booking_id,
            "amount": amount,
            "currency": currency
        }
    )

@app.get("/payments/cancel", response_class=HTMLResponse)
async def payment_cancel_page(
    request: Request, 
    booking_id: str = None,
    user=Depends(optional_user)
):
    return templates.TemplateResponse(
        "payment_cancel.html", 
        {
            "request": request, 
            "user": user,
            "booking_id": booking_id
        }
    )


# Log out clears coookies
@app.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("access_token")
    return response