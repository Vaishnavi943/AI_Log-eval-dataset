from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SampleRequest, LogOut
from app.services.sampling import sample_logs

router = APIRouter(prefix="/sampling", tags=["sampling"])


@router.post("/run", response_model=list[LogOut])
def run_sampling(req: SampleRequest, db: Session = Depends(get_db)):
    return sample_logs(db, req.mode, req.n)
