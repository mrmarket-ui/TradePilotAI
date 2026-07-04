from fastapi import APIRouter

router = APIRouter(
    prefix="/trading",
    tags=["Trading"]
)


@router.post("/sync")
def sync():

    return {
        "message": "Trade synchronization coming next."
    }