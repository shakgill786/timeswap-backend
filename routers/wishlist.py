from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
def view_wishlist(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Fetch all wishlist items for the logged-in user.
    """
    wishlist_items = (
        db.query(models.Wishlist, models.Product)
        .join(models.Product, models.Product.id == models.Wishlist.product_id)
        .filter(models.Wishlist.user_id == user.id)
        .all()
    )

    return [
        {
            "wishlist_id": item.Wishlist.id,
            "product": {
                "id": item.Product.id,
                "title": item.Product.title,
                "description": item.Product.description,
                "image": item.Product.image,
                "price": getattr(item.Product, "price", 0.0),
            }
        }
        for item in wishlist_items
    ]

@router.post("/{product_id}")
def add_to_wishlist(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Add a product to the user's wishlist.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ Prevent duplicate wishlist entries
    existing_item = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id, models.Wishlist.product_id == product_id).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Item already in wishlist")

    wishlist_item = models.Wishlist(user_id=user.id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    return {"message": f"Product '{product.title}' added to wishlist"}

@router.delete("/{wishlist_id}")
def remove_from_wishlist(wishlist_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Remove a product from the user's wishlist.
    """
    wishlist_item = db.query(models.Wishlist).filter(models.Wishlist.id == wishlist_id, models.Wishlist.user_id == user.id).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    db.delete(wishlist_item)
    db.commit()
    return {"message": "Product removed from wishlist"}
