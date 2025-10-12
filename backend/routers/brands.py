"""
═══════════════════════════════════════════════════════════════════════════
                                 BRANDS.PY
         BRANDS API ROUTER - HANDLES LISTING BRANDS AND RETRIEVING
           BRAND DETAILS INCLUDING LOGOS, IMAGES, AND BRAND VOICE DATA

ENDPOINTS:
    list_brands() -> RETURNS LIST OF ALL AVAILABLE BRANDS
    get_brand_details() -> RETURNS DETAILED INFORMATION FOR A SPECIFIC BRAND
═══════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException  # type: ignore
from schemas.responses import BrandsListResponse, BrandDetailsResponse
from pathlib import Path
import json
from typing import Dict, List

router = APIRouter(prefix="/brands", tags=["brands"])

DATA_DIR = Path(__file__).parent.parent / "data" / "clients"

@router.get("/list", response_model=BrandsListResponse)
async def list_brands():
    try:
        if not DATA_DIR.exists():
            raise HTTPException(
                status_code=404,
                detail="Brands directory not found"
            )
        
        brands = []
        for brand_dir in DATA_DIR.iterdir():
            if brand_dir.is_dir():
                brand_json_path = brand_dir / "brand.json"
                
                brand_name = brand_dir.name
                if brand_json_path.exists():
                    try:
                        with open(brand_json_path, 'r') as f:
                            brand_data = json.load(f)
                            if brand_data.get('brand_name'):
                                brand_name = brand_data['brand_name']
                    except Exception:
                        pass
                
                brands.append({
                    'brand_id': brand_dir.name,
                    'brand_name': brand_name
                })
        
        return BrandsListResponse(brands=brands)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list brands: {str(e)}"
        )


@router.get("/{brand_id}", response_model=BrandDetailsResponse)
async def get_brand_details(brand_id: str):
    try:
        brand_dir = DATA_DIR / brand_id
        
        if not brand_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Brand '{brand_id}' not found"
            )
        
        brand_json_path = brand_dir / "brand.json"
        
        if not brand_json_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"brand.json not found for brand '{brand_id}'"
            )
        
        with open(brand_json_path, 'r') as f:
            brand_data = json.load(f)
        
        logo_data = None
        if brand_data.get('logo'):
            logo_data = {
                'path': brand_data['logo']['path'],
                'full_path': f"/brand-assets/{brand_id}/{brand_data['logo']['path']}",
                'description': brand_data['logo'].get('description', '')
            }
        
        instagram_images = []
        if brand_data.get('instagram'):
            for img in brand_data['instagram']:
                instagram_images.append({
                    'path': img['path'],
                    'full_path': f"/brand-assets/{brand_id}/{img['path']}",
                    'description': img.get('description', ''),
                    'filename': Path(img['path']).name
                })
        
        return BrandDetailsResponse(
            brand_id=brand_id,
            brand_name=brand_data.get('brand_name', brand_id),
            industry=brand_data.get('industry', ''),
            logo=logo_data,
            instagram_images=instagram_images,
            brand_voice=brand_data.get('brand_voice', {}),
            target_audience=brand_data.get('target_audience', {}),
            messaging=brand_data.get('messaging', {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get brand details: {str(e)}"
        )
