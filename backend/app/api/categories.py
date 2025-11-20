from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter()

@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    return service.create_category(category)

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    return service.get_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    category = service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return None
