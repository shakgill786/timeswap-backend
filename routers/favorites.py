from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_favorites(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Fetch all favorite products of a user."""
    return db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).all()

@router.post("/{product_id}")
def add_to_favorites(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Add a product to favorites."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_favorite = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id, models.Wishlist.product_id == product_id).first()
    if existing_favorite:
        raise HTTPException(status_code=400, detail="Product already in favorites")

    favorite = models.Wishlist(user_id=user.id, product_id=product_id)
    db.add(favorite)
    db.commit()
    return {"message": "Product added to favorites"}

@router.delete("/{wishlist_id}")
def remove_from_favorites(wishlist_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Remove a product from favorites."""
    favorite = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id, models.Wishlist.user_id == user.id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"message": "Product removed from favorites"}
