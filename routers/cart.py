from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.auth import get_current_user


router = APIRouter()

@router.get("/")
def view_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Cart).filter(models.Cart.user_id == user.id).all()

@router.post("/{product_id}")
def add_to_cart(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cart_item = models.Cart(user_id=user.id, product_id=product_id, quantity=1)
    db.add(cart_item)
    db.commit()
    return {"message": "Product added to cart"}

@router.delete("/{cart_id}")
def remove_from_cart(cart_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cart_item = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Product removed from cart"}

@router.post("/checkout")
def checkout(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db.query(models.Cart).filter(models.Cart.user_id == user.id).delete()
    db.commit()
    return {"message": "Transaction completed"}
