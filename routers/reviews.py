from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.auth import get_current_user


router = APIRouter()

@router.get("/{product_id}/")
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()

@router.post("/{product_id}/", response_model=schemas.ReviewResponse)
def create_review(product_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    new_review = models.Review(product_id=product_id, user_id=user.id, **review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.put("/{review_id}/", response_model=schemas.ReviewResponse)
def update_review(review_id: int, review_data: schemas.ReviewCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    review = db.query(models.Review).filter(models.Review.id == review_id, models.Review.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    
    for key, value in review_data.dict().items():
        setattr(review, key, value)
    db.commit()
    return review

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    review = db.query(models.Review).filter(models.Review.id == review_id, models.Review.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    
    db.delete(review)
    db.commit()
    return {"message": "Review deleted"}
