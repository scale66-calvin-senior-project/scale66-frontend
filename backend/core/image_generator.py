"""
═══════════════════════════════════════════════════════════════════════════
                            IMAGE_GENERATOR.PY
        IMAGE GENERATION CORE LOGIC - HANDLES LOADING BRAND IMAGES,
          GENERATING IMAGES VIA GEMINI API, AND SAVING RESULTS TO DISK

FUNCTIONS:
    load_brand_image() -> LOADS BRAND IMAGE AS PIL IMAGE OBJECT
    load_brand_data() -> LOADS BRAND.JSON DATA FOR PROMPT ENHANCEMENT
    generate_images() -> GENERATES IMAGES USING GEMINI API AND SAVES TO DISK
    _generate_text_to_image() -> CREATES NEW IMAGE FROM TEXT PROMPT
    _generate_image_variations() -> CREATES IMAGE VARIATIONS FROM INPUT IMAGE
    _save_image_bytes() -> SAVES IMAGE BYTES TO BRAND DIRECTORY
    get_next_image_filename() -> FINDS NEXT AVAILABLE FILENAME
═══════════════════════════════════════════════════════════════════════════
"""

import json
from typing import Dict, Optional, Tuple
from pathlib import Path
from PIL import Image  # type: ignore
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from core.prompts import process_text_to_image_prompt, process_image_to_image_prompt


def load_brand_image(brand_id: str, image_path: str) -> Image.Image:
    data_dir = Path(__file__).parent.parent / "data" / "clients"
    full_image_path = data_dir / brand_id / image_path
    
    if not full_image_path.exists():
        raise FileNotFoundError(f"Image not found: {brand_id}/{image_path}")
    
    if not full_image_path.is_file():
        raise ValueError(f"Path is not a file: {brand_id}/{image_path}")
    
    try:
        return Image.open(full_image_path)
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")


def load_brand_data(brand_id: str) -> Optional[Dict]:
    try:
        data_dir = Path(__file__).parent.parent / "data" / "clients"
        brand_json_path = data_dir / brand_id / "brand.json"
        
        if not brand_json_path.exists():
            print(f"Warning: brand.json not found for {brand_id}")
            return None
        
        with open(brand_json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading brand data for {brand_id}: {str(e)}")
        return None


def generate_images(
    prompt: str,
    aspect_ratio: str,
    api_key: str,
    input_image_path: Optional[str] = None,
    brand_id: Optional[str] = None,
) -> Dict:
    if not brand_id:
        raise ValueError("brand_id is required for saving images")
    
    client = genai.Client(api_key=api_key)
    
    brand_data = load_brand_data(brand_id) if brand_id else None
    
    try:
        if input_image_path:
            final_prompt = process_image_to_image_prompt(prompt, brand_data)
            input_image = load_brand_image(brand_id, input_image_path)
            result = _generate_image_variations(client, final_prompt, aspect_ratio, input_image, brand_id)
        else:
            final_prompt = process_text_to_image_prompt(prompt, brand_data)
            result = _generate_text_to_image(client, final_prompt, aspect_ratio, brand_id)
        
        return result
        
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")


def _generate_text_to_image(client: genai.Client, prompt: str, aspect_ratio: str, brand_id: str) -> Dict:
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
        )
    )
    
    image_bytes = None
    for generated_image in response.generated_images:
        if generated_image.image is not None:
            image_bytes = generated_image.image.image_bytes
            break
    
    if image_bytes is None:
        raise Exception("No image data returned from Imagen API")
    
    saved_path = _save_image_bytes(brand_id, image_bytes, has_input_image=False)
    
    return {
        "saved_image_path": saved_path,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "status": "success",
        "input_image_provided": False,
    }


def _generate_image_variations(client: genai.Client, prompt: str, aspect_ratio: str, input_image: Image.Image, brand_id: str) -> Dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, input_image],
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            )
        )
    )
    
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_bytes = part.inline_data.data
            
            saved_path = _save_image_bytes(brand_id, image_bytes, has_input_image=True)
            
            return {
                "saved_image_path": saved_path,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "status": "success",
                "input_image_provided": True,
            }
        elif part.text is not None:
            print(f"Gemini response text: {part.text}")
    
    raise Exception("No image data returned from Gemini API")


def _save_image_bytes(brand_id: str, image_bytes: bytes, has_input_image: bool) -> str:
    data_dir = Path(__file__).parent.parent / "data" / "clients"
    brand_dir = data_dir / brand_id
    
    if not brand_dir.exists():
        raise ValueError(f"Brand directory not found: {brand_id}")
    
    prefix = "updated" if has_input_image else "initial"
    filename, _ = get_next_image_filename(brand_id, prefix)
    
    file_path = brand_dir / "instagram" / filename
    
    with open(file_path, 'wb') as f:
        f.write(image_bytes)
    
    return f"instagram/{filename}"


def get_next_image_filename(brand_id: str, prefix: str) -> Tuple[str, int]:
    data_dir = Path(__file__).parent.parent / "data" / "clients"
    instagram_dir = data_dir / brand_id / "instagram"
    
    instagram_dir.mkdir(parents=True, exist_ok=True)
    
    i = 1
    while True:
        filename = f"{prefix}_{i}.png"
        file_path = instagram_dir / filename
        if not file_path.exists():
            return filename, i
        i += 1



