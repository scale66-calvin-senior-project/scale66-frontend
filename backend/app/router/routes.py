"""
API Routes - FastAPI endpoint definitions for carousel pipeline operations.
Exposes REST API endpoints for creating carousels, checking pipeline status,
listing all pipelines, and health checks.

Main Endpoints:
    1. POST /carousel/create - Initiates new carousel generation pipeline
    2. GET /carousel/{pipeline_id} - Retrieves status and results for specific pipeline
    3. GET /carousels - Lists all pipelines with their current states
    4. GET /health - Returns service health status

Connections:
    - Uses: CarouselPipeline for all carousel operations
    - Uses models: CarouselRequest (input), PipelineResult (output)
    - Mounted at: /api/v1 prefix in main.py
    - Called by: Frontend, Streamlit app, or API clients
"""

from typing import Dict
import re
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from ..core.pipeline import CarouselPipeline
from ..core.config import settings
from ..models.pipeline import CarouselRequest, PipelineResult


router = APIRouter()
pipeline = CarouselPipeline()
logger = logging.getLogger(__name__)


# Waitlist Models
class WaitlistRequest(BaseModel):
    email: EmailStr
    contentType: str


class WaitlistResponse(BaseModel):
    success: bool
    message: str
    emailId: str | None = None


@router.post("/carousel/create", response_model=dict)
async def create_carousel(request: CarouselRequest):
    pipeline_id = await pipeline.start_pipeline(request)
    return {
        "pipeline_id": pipeline_id,
        "status": "started",
        "message": "Carousel generation pipeline started successfully",
    }


@router.get("/carousel/{pipeline_id}", response_model=PipelineResult)
async def get_carousel_status(pipeline_id: str):
    result = pipeline.get_pipeline_status(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result


@router.get("/carousels", response_model=Dict[str, PipelineResult])
async def list_carousels():
    return pipeline.list_pipelines()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "carousel-pipeline-backend"}


@router.post("/waitlist", response_model=WaitlistResponse)
async def submit_waitlist(request: WaitlistRequest):
    """
    Submit email to waitlist - adds contact to Resend audience and sends welcome email.
    
    Args:
        request: WaitlistRequest containing email and contentType
        
    Returns:
        WaitlistResponse with success status, message, and optional email ID
    """
    try:
        # Import resend here to avoid issues if not installed
        import resend
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Resend library not installed. Run: pip install resend"
        )
    
    # Validate API key
    if not settings.resend_api_key:
        raise HTTPException(
            status_code=500,
            detail="RESEND_API_KEY environment variable is not set"
        )
    
    # Configure Resend client
    resend.api_key = settings.resend_api_key
    
    # Add contact to Resend audience
    if settings.resend_audience_id:
        try:
            contact_result = resend.Contacts.create(
                audience_id=settings.resend_audience_id,
                email=request.email,
                unsubscribed=False,
            )
            logger.info(f"✅ Successfully added {request.email} to Resend audience {settings.resend_audience_id}")
            logger.info(f"Contact ID: {contact_result.get('id', 'N/A')}")
        except Exception as contact_error:
            error_msg = str(contact_error)
            logger.error(f"❌ Error adding contact to Resend: {error_msg}")
            
            # If contact already exists, continue to send email
            if "already exists" not in error_msg.lower():
                logger.warning("⚠️ Continuing to send email despite contact creation error")
    else:
        logger.warning("⚠️ RESEND_AUDIENCE_ID not set - contact will not be added to an audience")
    
    # Send welcome email
    try:
        email_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
          <h1 style="color: #1a1a1a; font-size: 28px; margin-bottom: 10px;">Hey there!</h1>
          
          <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            Thanks so much for joining the Scale66 waitlist – we're genuinely excited to have you here!
          </p>
          
          <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            I know you're probably busy building your startup, which is exactly why we created Scale66. We're building an AI-powered marketing platform that helps software founders like you turn attention into paying customers through organic content that actually works.
          </p>
          
          <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            As we get closer to launch, we'll keep you in the loop with:
          </p>
          
          <ul style="font-size: 16px; line-height: 1.8; margin-bottom: 20px; padding-left: 24px;">
            <li>Early access opportunities</li>
            <li>Exclusive updates on new features</li>
            <li>Tips and insights from other founders</li>
            <li>Behind-the-scenes peeks at what we're building</li>
          </ul>
          
          <p style="font-size: 16px; line-height: 1.6; margin-bottom: 16px;">
            In the meantime, if you have any questions or just want to say hi, feel free to reply to this email. We read every message and love hearing from our community.
          </p>
          
          <p style="font-size: 16px; line-height: 1.6; margin-bottom: 8px;">
            Looking forward to building something amazing together,
          </p>
          
          <p style="font-size: 16px; line-height: 1.6; margin-top: 0;">
            <strong>The Scale66 Team</strong><br>
            <span style="color: #666; font-size: 14px;">hello@scale66.com</span>
          </p>
        </div>
        """
        
        email_result = resend.Emails.send({
            "from": "Scale66 <hello@scale66.com>",
            "to": [request.email],
            "subject": "Welcome to Scale66 – You're on the list!",
            "html": email_html,
        })
        
        logger.info(f"✅ Welcome email sent successfully to {request.email}")
        
        email_id = email_result.get("id")
        if email_id:
            logger.info(f"Email ID: {email_id}")
        else:
            logger.warning("⚠️ Resend API call succeeded but no email ID returned")
        
        return WaitlistResponse(
            success=True,
            message="Successfully added to waitlist and email sent",
            emailId=email_id
        )
        
    except Exception as email_error:
        error_msg = str(email_error)
        logger.error(f"❌ Error sending welcome email: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send welcome email: {error_msg}"
        )

