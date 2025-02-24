from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.auth import get_current_user

router = APIRouter()

### 🚀 GET All Products ###
@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db), query: str = None):
    """
    Fetch all products. Optionally, filter by query.
    """
    if query:
        return db.query(models.Product).filter(models.Product.title.contains(query)).all()
    return db.query(models.Product).all()

### 🚀 CREATE Product ###
@router.post("/", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Create a new product.
    """
    new_product = models.Product(**product.dict(), owner_id=user.id)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

### 🚀 UPDATE Product ###
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Update a product if the user owns it.
    """
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id, models.Product.owner_id == user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")

    for key, value in product_data.dict().items():
        setattr(product, key, value)
    db.commit()
    return product

### 🚀 DELETE Product ###
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Delete a product if the user owns it.
    """
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id, models.Product.owner_id == user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
