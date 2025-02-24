from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.auth import get_current_user


router = APIRouter()

@router.get("/")
def view_wishlist(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).all()

@router.post("/{product_id}")
def add_to_wishlist(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    wishlist_item = models.Wishlist(user_id=user.id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    return {"message": "Product added to wishlist"}

@router.delete("/{wishlist_id}")
def remove_from_wishlist(wishlist_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    wishlist_item = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id, models.Wishlist.user_id == user.id).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    db.delete(wishlist_item)
    db.commit()
    return {"message": "Product removed from wishlist"}
