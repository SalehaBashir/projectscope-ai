from fastapi import APIRouter

from app.ml.model_registry import get_model_info


router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"],
)


@router.get("/model")
def get_active_model():
    return get_model_info()