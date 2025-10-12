"""
═══════════════════════════════════════════════════════════════════════════
                          CLEANUP_BRAND_JSON.PY
        UTILITY SCRIPT TO REMOVE DUPLICATE ENTRIES AND INVALID IMAGE
                      REFERENCES FROM BRAND.JSON FILES

FUNCTIONS:
    cleanup_brand_json() -> CLEANS UP A SINGLE BRAND'S JSON FILE
    cleanup_all_brands() -> CLEANS UP ALL BRANDS IN THE SYSTEM
    main() -> PARSES ARGUMENTS AND RUNS CLEANUP
═══════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict


def cleanup_brand_json(brand_id: str, dry_run: bool = False) -> bool:
    try:
        data_dir = Path(__file__).parent.parent / "data" / "clients"
        brand_dir = data_dir / brand_id
        brand_json_path = brand_dir / "brand.json"
        
        if not brand_dir.exists():
            print(f"❌ Brand directory not found: {brand_id}")
            return False
        
        if not brand_json_path.exists():
            print(f"❌ brand.json not found for: {brand_id}")
            return False
        
        print(f"\n🔍 Analyzing {brand_id}/brand.json...")
        
        with open(brand_json_path, 'r') as f:
            brand_data = json.load(f)
        
        if "instagram" not in brand_data:
            print("   No instagram images found")
            return True
        
        original_images = brand_data["instagram"]
        original_count = len(original_images)
        
        print(f"   Original entries: {original_count}")
        
        seen_paths = set()
        cleaned_images = []
        duplicates_removed = 0
        invalid_removed = 0
        
        for img in original_images:
            path = img.get("path")
            
            if not path:
                print(f"   ⚠️  Skipping entry with no path")
                continue
            
            if path in seen_paths:
                duplicates_removed += 1
                print(f"   🗑️  Duplicate: {path}")
                continue
            
            full_path = brand_dir / path
            if not full_path.exists():
                invalid_removed += 1
                print(f"   🗑️  File not found: {path}")
                continue
            
            seen_paths.add(path)
            cleaned_images.append(img)
        
        removed_count = duplicates_removed + invalid_removed
        final_count = len(cleaned_images)
        
        print(f"\n📊 Summary:")
        print(f"   Original entries:    {original_count}")
        print(f"   Duplicates removed:  {duplicates_removed}")
        print(f"   Invalid removed:     {invalid_removed}")
        print(f"   Final entries:       {final_count}")
        
        if removed_count == 0:
            print(f"\n✅ No cleanup needed for {brand_id}")
            return True
        
        if dry_run:
            print(f"\n🔍 Dry run - no changes saved")
            return True
        
        brand_data["instagram"] = cleaned_images
        
        with open(brand_json_path, 'w') as f:
            json.dump(brand_data, f, indent="\t")
        
        print(f"\n✅ Cleaned up {brand_id}/brand.json")
        print(f"   Removed {removed_count} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up {brand_id}: {str(e)}")
        return False


def cleanup_all_brands(dry_run: bool = False):
    data_dir = Path(__file__).parent.parent / "data" / "clients"
    
    if not data_dir.exists():
        print(f"❌ Brands directory not found: {data_dir}")
        return
    
    brands = [d.name for d in data_dir.iterdir() if d.is_dir()]
    
    if not brands:
        print("No brands found")
        return
    
    print(f"Found {len(brands)} brand(s): {', '.join(brands)}")
    
    success_count = 0
    for brand_id in brands:
        if cleanup_brand_json(brand_id, dry_run):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processed {len(brands)} brand(s), {success_count} successful")


def main():
    parser = argparse.ArgumentParser(
        description='Cleanup brand.json files by removing duplicates and invalid references',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_brand_json.py thehiverapp
  python cleanup_brand_json.py thehiverapp --dry-run
  python cleanup_brand_json.py --all
        """
    )
    
    parser.add_argument(
        'brand_id',
        type=str,
        nargs='?',
        help='Brand ID to clean up (omit if using --all)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean up all brands'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without saving'
    )
    
    args = parser.parse_args()
    
    if args.all:
        cleanup_all_brands(args.dry_run)
    elif args.brand_id:
        cleanup_brand_json(args.brand_id, args.dry_run)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
