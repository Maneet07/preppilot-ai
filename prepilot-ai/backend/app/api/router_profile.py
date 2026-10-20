from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.schemas import ProfileCreate, ProfileUpdate, ProfileResponse, ApiResponse
from app.core.auth import get_current_user
from app.database import get_db, Profile

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.get("/", response_model=ProfileResponse, summary="Get current user profile")
async def get_profile(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's profile."""
    # Look up profile by user ID
    profile = db.query(Profile).filter(Profile.id == user["id"]).first()
    if not profile:
        # Create a basic profile if none exists
        profile = Profile(
            id=user["id"],
            email=user.get("email", ""),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/", response_model=ProfileResponse, summary="Update user profile")
async def update_profile(
    profile_data: ProfileUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile."""
    profile = db.query(Profile).filter(Profile.id == user["id"]).first()
    if not profile:
        profile = Profile(id=user["id"], email=user.get("email", ""))
        db.add(profile)
    
    update_dict = profile_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)
    
    profile.updated_at = datetime.now(profile.updated_at.tzinfo) if profile.updated_at else datetime.now()
    db.commit()
    db.refresh(profile)
    return profile