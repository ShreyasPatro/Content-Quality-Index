"""API router aggregation."""

from fastapi import APIRouter

from app.api import approvals, auth, blogs, evaluations, reviews, rewrites, versions, sandbox

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(blogs.router, tags=["blogs"])
api_router.include_router(versions.router, tags=["versions"])
api_router.include_router(evaluations.router, tags=["evaluations"])
api_router.include_router(rewrites.router, tags=["rewrites"])
api_router.include_router(reviews.router, tags=["reviews"])
api_router.include_router(approvals.router, tags=["approvals"])
api_router.include_router(sandbox.router, prefix="/sandbox", tags=["sandbox"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
