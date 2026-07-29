from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.repositories.review_repo import ReviewRepository
from app.repositories.customer_repo import CustomerRepository
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewResponse])
def product_reviews(product_id: int, db: Session = Depends(get_db)):
    return ReviewRepository(db).list_by_product(product_id)


@router.get("/", response_model=list[ReviewResponse])
def list_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    return ReviewRepository(db).list_all()


@router.post("/", response_model=ReviewResponse)
def create_review(
    body: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repo = ReviewRepository(db)
    customer = CustomerRepository(db).get_by_user_id(user.id)
    if not customer:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer profile required")
    return repo.create(product_id=body.product_id, customer_id=customer.id, rating=body.rating, text=body.text)


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    body: ReviewUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("super_admin", "admin")),
):
    repo = ReviewRepository(db)
    review = repo.get_by_id(review_id)
    if not review:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return repo.update(review, **body.model_dump(exclude_unset=True))
