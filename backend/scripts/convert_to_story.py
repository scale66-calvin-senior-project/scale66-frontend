"""
═══════════════════════════════════════════════════════════════════════════
                           CONVERT_TO_STORY.PY
       IMAGE ASPECT RATIO CONVERTER - CONVERTS IMAGES TO 9:16 FORMAT
          FOR INSTAGRAM STORIES/REELS WITH HIGH QUALITY PRESERVATION

FUNCTIONS:
    convert_image() -> CONVERTS IMAGE TO 9:16 ASPECT RATIO
    detect_brand_id() -> DETECTS BRAND ID FROM IMAGE PATH
    update_brand_json_with_converted_image() -> UPDATES BRAND.JSON WITH CONVERTED IMAGE
    main() -> PARSES ARGUMENTS AND RUNS CONVERSION
═══════════════════════════════════════════════════════════════════════════
"""

import argparse
import sys
import json
from pathlib import Path
from PIL import Image, ImageOps  # type: ignore
from typing import Tuple, Optional


TARGET_RATIO = 9 / 16

QUALITY_PRESETS = {
    'standard': {'width': 1080, 'height': 1920, 'compression': 6},
    'high': {'width': 1080, 'height': 1920, 'compression': 3},
    'ultra': {'width': 2160, 'height': 3840, 'compression': 1},
}


def get_next_filename(directory: Path) -> Tuple[Path, int]:
    i = 1
    while True:
        filename = f"insta_image_{i}.png"
        file_path = directory / filename
        if not file_path.exists():
            return file_path, i
        i += 1


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def scale_to_aspect_ratio(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def pad_to_aspect_ratio(image: Image.Image, target_width: int, target_height: int, 
                        bg_color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    current_width, current_height = image.size
    current_ratio = current_width / current_height
    target_ratio = target_width / target_height
    
    if abs(current_ratio - target_ratio) < 0.01:
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    if current_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / current_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * current_ratio)
    
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    result = Image.new('RGB', (target_width, target_height), bg_color)
    
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    
    if resized.mode == 'RGBA':
        result.paste(resized, (x, y), resized)
    else:
        result.paste(resized, (x, y))
    
    return result


def detect_brand_id(image_path: Path) -> Optional[str]:
    try:
        parts = image_path.parts
        if 'clients' in parts:
            clients_idx = parts.index('clients')
            if clients_idx + 1 < len(parts):
                return parts[clients_idx + 1]
    except (ValueError, IndexError):
        pass
    return None


def update_brand_json_with_converted_image(brand_id: str, image_relative_path: str, original_image: str):
    try:
        script_dir = Path(__file__).parent
        brand_dir = script_dir.parent / "data" / "clients" / brand_id
        brand_json_path = brand_dir / "brand.json"
        
        if not brand_json_path.exists():
            print(f"   ⚠️  brand.json not found for {brand_id}, skipping update")
            return
        
        with open(brand_json_path, 'r') as f:
            brand_data = json.load(f)
        
        if "instagram" not in brand_data:
            brand_data["instagram"] = []
        
        existing_paths = [img.get("path") for img in brand_data["instagram"]]
        if image_relative_path in existing_paths:
            print(f"   ℹ️  Image already in brand.json: {image_relative_path}")
            return
        
        new_image = {
            "path": image_relative_path,
            "description": f"9:16 conversion of {original_image}"
        }
        
        brand_data["instagram"].append(new_image)
        
        with open(brand_json_path, 'w') as f:
            json.dump(brand_data, f, indent="\t")
        
        print(f"   ✅ Updated brand.json: Added {image_relative_path}")
        
    except Exception as e:
        print(f"   ⚠️  Failed to update brand.json: {str(e)}")


def convert_image(input_path: Path, method: str = 'scale', 
                  bg_color: str = '#000000', quality: str = 'high') -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"Image not found: {input_path}")
    
    if not input_path.is_file():
        raise ValueError(f"Not a file: {input_path}")
    
    if quality not in QUALITY_PRESETS:
        raise ValueError(f"Invalid quality: {quality}. Use 'standard', 'high', or 'ultra'")
    
    settings = QUALITY_PRESETS[quality]
    target_width = settings['width']
    target_height = settings['height']
    compression = settings['compression']
    
    print(f"📷 Loading image: {input_path}")
    try:
        image = Image.open(input_path)
        original_width, original_height = image.size
        original_ratio = original_width / original_height
        print(f"   Original size: {original_width}x{original_height} ({original_ratio:.2f}:1)")
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")
    
    if image.mode in ('RGBA', 'LA', 'P'):
        if method == 'scale':
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA' or image.mode == 'LA':
                rgb_image.paste(image, mask=image.split()[-1])
            else:
                rgb_image.paste(image)
            image = rgb_image
        elif method == 'pad':
            if image.mode == 'P':
                image = image.convert('RGBA')
    
    target_ratio = target_width / target_height
    print(f"🔄 Converting to 9:16 aspect ratio ({target_width}x{target_height}) using '{method}' method...")
    print(f"   Quality: {quality} (compression level: {compression})")
    
    if method == 'scale':
        converted = scale_to_aspect_ratio(image, target_width, target_height)
        ratio_diff = abs(original_ratio - target_ratio)
        if ratio_diff > 0.1:
            print(f"   ⚠️  Note: Image will be stretched to fit (aspect ratio changed by {ratio_diff:.2f})")
    elif method == 'pad':
        rgb_color = hex_to_rgb(bg_color)
        converted = pad_to_aspect_ratio(image, target_width, target_height, rgb_color)
        print(f"   Padding color: {bg_color}")
    else:
        raise ValueError(f"Invalid method: {method}. Use 'scale' or 'pad'")
    
    output_path, index = get_next_filename(input_path.parent)
    
    print(f"💾 Saving to: {output_path}")
    converted.save(
        output_path, 
        'PNG', 
        optimize=False,
        compress_level=compression
    )
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Success! Saved as {output_path.name} ({file_size_mb:.2f} MB)")
    
    brand_id = detect_brand_id(input_path)
    if brand_id:
        print(f"\n📝 Updating brand data...")
        print(f"   Detected brand: {brand_id}")
        
        try:
            parts = output_path.parts
            if 'instagram' in parts:
                instagram_idx = parts.index('instagram')
                relative_path = '/'.join(parts[instagram_idx:])
                update_brand_json_with_converted_image(brand_id, relative_path, input_path.name)
        except Exception as e:
            print(f"   ⚠️  Could not determine relative path: {str(e)}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert images to 9:16 aspect ratio for Instagram Stories/Reels with high quality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_to_story.py ./image.jpg
  python convert_to_story.py ./image.jpg --method pad --bg-color '#FFFFFF'
  python convert_to_story.py ./image.png --quality ultra
  python convert_to_story.py ./image.jpg --method scale --quality high
        """
    )
    
    parser.add_argument(
        'image_path',
        type=str,
        help='Path to the input image'
    )
    
    parser.add_argument(
        '--method',
        type=str,
        choices=['scale', 'pad'],
        default='scale',
        help='Conversion method: scale (stretch to fit, preserves all content) or pad (add borders). Default: scale'
    )
    
    parser.add_argument(
        '--quality',
        type=str,
        choices=['standard', 'high', 'ultra'],
        default='high',
        help='Quality preset: standard (1080x1920), high (1080x1920, low compression), ultra (2160x3840, 4K). Default: high'
    )
    
    parser.add_argument(
        '--bg-color',
        type=str,
        default='#000000',
        help='Background color for padding method (hex format, e.g., #000000). Default: #000000 (black)'
    )
    
    args = parser.parse_args()
    
    try:
        input_path = Path(args.image_path).resolve()
        output_path = convert_image(input_path, args.method, args.bg_color, args.quality)
        print(f"\n🎉 Conversion complete!")
        print(f"   Input:  {input_path}")
        print(f"   Output: {output_path}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
