from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithStats,
    SubcategoryCreate, SubcategoryResponse
)
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories for the current user"""
    service = CategoryService(db)
    return service.get_categories(current_user.id, include_inactive)


@router.get("/with-stats", response_model=List[dict])
def get_categories_with_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories with expense statistics"""
    service = CategoryService(db)
    return service.get_categories_with_stats(current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific category"""
    service = CategoryService(db)
    category = service.get_category_by_id(category_id, current_user.id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    service = CategoryService(db)
    return service.create_category(category, current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a category (rename, activate/deactivate)"""
    service = CategoryService(db)
    updated = service.update_category(category_id, current_user.id, category_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return updated


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category (sets inactive)"""
    service = CategoryService(db)
    success = service.delete_category(category_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


@router.post("/merge", status_code=status.HTTP_200_OK)
def merge_categories(
    source_id: int,
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Merge source category into target category"""
    service = CategoryService(db)
    success = service.merge_categories(source_id, target_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot merge categories. Check that both exist and belong to you."
        )
    return {"message": "Categories merged successfully"}


@router.get("/{category_id}/subcategories", response_model=List[SubcategoryResponse])
def get_subcategories(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subcategories for a category"""
    service = CategoryService(db)
    return service.get_subcategories(category_id, current_user.id)


@router.post("/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(
    subcategory: SubcategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subcategory"""
    service = CategoryService(db)
    created = service.create_subcategory(subcategory, current_user.id)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found"
        )
    return created


@router.delete("/subcategories/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subcategory(
    subcategory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a subcategory (sets inactive)"""
    service = CategoryService(db)
    success = service.delete_subcategory(subcategory_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found"
        )
