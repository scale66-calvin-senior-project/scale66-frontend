"""
═══════════════════════════════════════════════════════════════════════════
                            IMAGE_GENERATOR.PY
        IMAGE GENERATION CORE LOGIC - HANDLES LOADING BRAND IMAGES,
          GENERATING IMAGES VIA GEMINI API, AND SAVING RESULTS TO DISK

FUNCTIONS:
    load_brand_image() -> LOADS AND ENCODES BRAND IMAGE TO BASE64
    load_brand_data() -> LOADS BRAND.JSON DATA FOR PROMPT ENHANCEMENT
    generate_images() -> GENERATES IMAGES USING GEMINI API
    save_generated_image() -> SAVES GENERATED IMAGE TO BRAND DIRECTORY
    update_brand_json() -> UPDATES BRAND.JSON WITH NEW IMAGE ENTRY
═══════════════════════════════════════════════════════════════════════════
"""

import base64
import io
import json
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from PIL import Image  # type: ignore
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from core.prompts import process_prompt


def load_brand_image(brand_id: str, image_path: str) -> str:
    data_dir = Path(__file__).parent.parent / "data" / "clients"
    full_image_path = data_dir / brand_id / image_path
    
    if not full_image_path.exists():
        raise FileNotFoundError(f"Image not found: {brand_id}/{image_path}")
    
    if not full_image_path.is_file():
        raise ValueError(f"Path is not a file: {brand_id}/{image_path}")
    
    try:
        with open(full_image_path, 'rb') as image_file:
            image_bytes = image_file.read()
            return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to read or encode image: {str(e)}")


def load_brand_data(brand_id: str) -> Optional[Dict]:
    """Loads brand.json data for the given brand_id"""
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
    input_image: Optional[str] = None,
    brand_id: Optional[str] = None,
) -> Dict:
    client = genai.Client(api_key=api_key)
    
    is_image_editing = input_image is not None
    
    # Load brand data if brand_id is provided
    brand_data = load_brand_data(brand_id) if brand_id else None
    
    # Pass brand_data to process_prompt
    final_prompt = process_prompt(
        prompt, 
        has_input_image=is_image_editing,
        brand_data=brand_data
    )
    
    try:
        if is_image_editing:
            result = _generate_image_variations(client, final_prompt, aspect_ratio, input_image, brand_id, brand_data)
        else:
            result = _generate_text_to_image(client, final_prompt, aspect_ratio)
        
        return result
        
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")


def _generate_text_to_image(client: genai.Client, prompt: str, aspect_ratio: str) -> Dict:
    response = client.models.generate_images(
        model="imagen-4.0-ultra-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
        )
    )
    
    image_base64 = None
    for generated_image in response.generated_images:
        if generated_image.image is not None:
            # Access the image bytes correctly according to the API
            image_bytes = generated_image.image.image_bytes
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            break
    
    if image_base64 is None:
        raise Exception("No image data returned from Imagen API")
    
    return {
        "images": [{
            "image_data": image_base64,
            "index": 0
        }],
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "status": "success",
        "input_image_provided": False,
        "default_image_used": False
    }


def _generate_image_variations(client: genai.Client, prompt: str, aspect_ratio: str, input_image_base64: str, brand_id: Optional[str] = None, brand_data: Optional[Dict] = None) -> Dict:
    try:
        if "base64," in input_image_base64:
            input_image_base64 = input_image_base64.split("base64,")[1]
        
        image_bytes = base64.b64decode(input_image_base64)
        input_image = Image.open(io.BytesIO(image_bytes))
        
    except Exception as e:
        raise ValueError(f"Failed to decode input image: {str(e)}")
    
    # Load brand logo if available
    logo_image = None
    if brand_id and brand_data and "logo" in brand_data:
        try:
            logo_path = brand_data["logo"]["path"]
            logo_base64 = load_brand_image(brand_id, logo_path)
            
            if "base64," in logo_base64:
                logo_base64 = logo_base64.split("base64,")[1]
            
            logo_bytes = base64.b64decode(logo_base64)
            logo_image = Image.open(io.BytesIO(logo_bytes))
            print(f"✅ Loaded brand logo: {logo_path}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to load brand logo: {str(e)}")
            # Continue without logo if it fails to load
    
    try:
        # Build contents array - include logo if available
        contents = [prompt]
        if logo_image:
            contents.append(logo_image)
        contents.append(input_image)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                )
            )
        )
        
        image_base64 = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"Gemini response text: {part.text}")
            elif part.inline_data is not None:
                image_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                break
        
        if image_base64 is None:
            raise Exception("No image data returned from Gemini API")
        
    except Exception as e:
        raise Exception(f"Image editing failed: {str(e)}")
    
    return {
        "images": [{
            "image_data": image_base64,
            "index": 0
        }],
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "status": "success",
        "input_image_provided": True,
    }


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


def save_generated_image(brand_id: str, image_base64: str, has_input_image: bool, prompt: str) -> Optional[str]:
    try:
        data_dir = Path(__file__).parent.parent / "data" / "clients"
        brand_dir = data_dir / brand_id
        
        if not brand_dir.exists():
            raise ValueError(f"Brand directory not found: {brand_id}")
        
        prefix = "updated" if has_input_image else "initial"
        
        filename, index = get_next_image_filename(brand_id, prefix)
        
        image_bytes = base64.b64decode(image_base64)
        file_path = brand_dir / "instagram" / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        relative_path = f"instagram/{filename}"
        
        update_brand_json(brand_id, relative_path, prompt)
        
        return relative_path
        
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None


def update_brand_json(brand_id: str, image_path: str, description: str = "", brand_message: str = ""):
    try:
        data_dir = Path(__file__).parent.parent / "data" / "clients"
        brand_json_path = data_dir / brand_id / "brand.json"
        
        if not brand_json_path.exists():
            raise ValueError(f"brand.json not found for {brand_id}")
        
        with open(brand_json_path, 'r') as f:
            brand_data = json.load(f)
        
        if "instagram" not in brand_data:
            brand_data["instagram"] = []
        
        existing_paths = [img.get("path") for img in brand_data["instagram"]]
        if image_path in existing_paths:
            for img in brand_data["instagram"]:
                if img.get("path") == image_path:
                    img["visual_description"] = description
                    img["brand_message"] = brand_message
                    print(f"✅ Updated existing entry in brand.json for {brand_id}: {image_path}")
                    break
        else:
            new_image = {
                "path": image_path,
                 "visual_description": description,
                 "brand_message": brand_message
            }
            brand_data["instagram"].append(new_image)
            print(f"✅ Added new entry to brand.json for {brand_id}: {image_path}")
        
        with open(brand_json_path, 'w') as f:
            json.dump(brand_data, f, indent="\t")
        
    except Exception as e:
        print(f"Error updating brand.json: {str(e)}")
