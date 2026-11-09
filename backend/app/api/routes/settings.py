from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import UserSetting
from app.schemas.schemas import UserSettingResponse, UserSettingUpdate

router = APIRouter(prefix="/settings", tags=["User Settings"])

@router.get("/", response_model=UserSettingResponse)
def get_user_settings(db: Session = Depends(get_db)):
    """Retrieve current company configuration and user preferences."""
    setting = db.query(UserSetting).first()
    if not setting:
        setting = UserSetting()
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting

@router.put("/", response_model=UserSettingResponse)
def update_user_settings(data: UserSettingUpdate, db: Session = Depends(get_db)):
    """Update company details, branding, default language and prompts."""
    setting = db.query(UserSetting).first()
    if not setting:
        setting = UserSetting()
        db.add(setting)

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(setting, key, value)

    db.commit()
    db.refresh(setting)
    return setting

