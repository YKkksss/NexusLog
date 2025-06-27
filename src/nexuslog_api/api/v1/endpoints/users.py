from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from nexuslog_api import crud, models, schemas
from nexuslog_api.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Delete a user.
    """
    user = await crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = await crud.user.remove(db=db, id=user_id)
    return deleted_user
