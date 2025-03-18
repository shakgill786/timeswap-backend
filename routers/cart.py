from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
def view_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Retrieve all items in the user's cart with full product details.
    """
    cart_items = (
        db.query(models.Cart, models.Product)
        .join(models.Product, models.Product.id == models.Cart.product_id)
        .filter(models.Cart.user_id == user.id)
        .all()
    )

    return [
        {
            "cart_id": item.Cart.id,
            "product": {
                "id": item.Product.id,
                "title": item.Product.title,
                "description": item.Product.description,
                "category": item.Product.category,
                "image": item.Product.image,
                "barter_options": item.Product.barter_options,
                "price": getattr(item.Product, "price", "N/A"),  # ✅ Ensure price exists
            },
            "quantity": item.Cart.quantity
        }
        for item in cart_items
    ]

@router.post("/{product_id}")
def add_to_cart(product_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Add a product to the user's shopping cart.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ✅ Prevent duplicates in cart
    existing_item = db.query(models.Cart).filter(models.Cart.user_id == user.id, models.Cart.product_id == product_id).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Product already exists in cart")

    cart_item = models.Cart(user_id=user.id, product_id=product_id, quantity=1)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)  # ✅ Ensure cart item is committed before returning

    return {"message": f"Product '{product.title}' added to cart", "cart_id": cart_item.id}

@router.put("/{cart_id}")
def update_cart_quantity(cart_id: int, quantity: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Update the quantity of an item in the user's shopping cart.
    """
    cart_item = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)  # ✅ Ensure updated value is returned

    return {"message": "Cart updated", "cart_id": cart_id, "quantity": cart_item.quantity}

@router.delete("/{cart_id}")
def remove_from_cart(cart_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """
    Remove a product from the user's shopping cart.
    """
    cart_item = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    db.delete(cart_item)
    db.commit()
    
    return {"message": "Product removed from cart"}
