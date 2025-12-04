import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel


class TemplateMetadata(BaseModel):
    id: str
    num_slides: int
    carousel_format: str
    description: str


class TemplateServiceError(Exception):
    pass


class TemplateService:
    _instance: Optional['TemplateService'] = None
    _templates: Optional[Dict[str, TemplateMetadata]] = None
    _templates_dir: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._templates is None:
            self._templates_dir = Path(__file__).parent.parent.parent / "templates"
            self._load_templates()
    
    def _load_templates(self) -> None:
        metadata_path = self._templates_dir / "templates.json"
        
        if not metadata_path.exists():
            self._templates = {}
            return
        
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
            
            self._templates = {
                t["id"]: TemplateMetadata(**t)
                for t in data.get("templates", [])
            }
            
        except Exception as e:
            raise TemplateServiceError(f"Template loading failed: {e}")
    
    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        return self._templates.get(template_id)
    
    def get_templates_for_format(self, carousel_format: str) -> List[TemplateMetadata]:
        return [
            t for t in self._templates.values()
            if t.carousel_format == carousel_format
        ]
    
    def get_template_image_base64(
        self, 
        template_id: str, 
        slide_number: int = 1
    ) -> str:
        image_path = self._templates_dir / template_id / f"{slide_number}.png"
        
        if not image_path.exists():
            raise TemplateServiceError(f"Template image not found: {image_path}")
        
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def list_all_templates(self) -> List[TemplateMetadata]:
        return list(self._templates.values())


template_service = TemplateService()
