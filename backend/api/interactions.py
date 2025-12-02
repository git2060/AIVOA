from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
# FIX: Confirmed imports are correct for the structured logging endpoint
from models.schemas import HCPInteractionCreate, HCPInteractionRead
from models.database import HCPInteraction
from database.setup import get_db_session

router = APIRouter()

# Endpoint for structured form submission 
@router.post("/log_form", response_model=HCPInteractionRead, status_code=status.HTTP_201_CREATED)
async def log_form_interaction(
    interaction_data: HCPInteractionCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Handles logging of an HCP interaction submitted via the structured form interface.
    Performs asynchronous database insertion.
    """
    try:
        # Convert Pydantic model to ORM model
        db_record = HCPInteraction.model_validate(interaction_data)
        
        session.add(db_record)
        await session.commit()
        await session.refresh(db_record)
        
        return db_record
        
    except Exception as e:
        # This will trigger the rollback in the get_db_session dependency
        raise HTTPException(status_code=500, detail=f"Database error during form log: {e}")