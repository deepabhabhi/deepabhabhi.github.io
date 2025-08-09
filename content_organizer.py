#!/usr/bin/env python3
"""
Content Organizer Script
Combines content organization and image list generation functionality.
1. Converts all image files in the content folder to WebP format and renames them sequentially
2. Generates a JSON file with all images for dynamic loading in the web interface
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from PIL import Image

def is_image_file(file_path):
    """Check if file is a supported image format"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
    return file_path.suffix.lower() in image_extensions

def convert_to_webp(input_path, output_path, quality=85):
    """Convert image to WebP format"""
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary (WebP doesn't support transparency in all cases)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save as WebP
            img.save(output_path, 'WEBP', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

def organize_content():
    """Main function to organize content folder"""
    content_dir = Path("content")
    
    if not content_dir.exists():
        print("Content folder not found!")
        return False
    
    # Get all image files
    image_files = []
    for file_path in content_dir.iterdir():
        if file_path.is_file() and is_image_file(file_path):
            image_files.append(file_path)
    
    if not image_files:
        print("No image files found in content folder!")
        return False
    
    print(f"Found {len(image_files)} image files to process...")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        converted_files = []
        
        # Convert all images to WebP
        for i, file_path in enumerate(image_files, 1):
            print(f"Processing {file_path.name}...")
            
            temp_output = temp_path / f"image_{i}.webp"
            
            if file_path.suffix.lower() == '.webp':
                # If already WebP, just copy
                shutil.copy2(file_path, temp_output)
                converted_files.append(temp_output)
            else:
                # Convert to WebP
                if convert_to_webp(file_path, temp_output):
                    converted_files.append(temp_output)
                else:
                    print(f"Failed to convert {file_path.name}")
                    continue
        
        # Remove original files
        print("\nRemoving original files...")
        for file_path in image_files:
            try:
                file_path.unlink()
                print(f"Removed: {file_path.name}")
            except Exception as e:
                print(f"Error removing {file_path.name}: {str(e)}")
        
        # Move converted files to content directory
        print("\nMoving converted files...")
        for temp_file in converted_files:
            final_path = content_dir / temp_file.name
            shutil.move(str(temp_file), str(final_path))
            print(f"Created: {final_path.name}")
    
    print(f"\nContent organization complete! {len(converted_files)} images converted and renamed.")
    return True

def get_image_files_for_json(content_dir):
    """Get all image files from the content directory for JSON generation"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp', '.svg'}
    image_files = []
    
    if not content_dir.exists():
        print(f"Content directory '{content_dir}' not found!")
        return []
    
    for file_path in content_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            # Store relative path for web use
            relative_path = f"content/{file_path.name}"
            image_files.append(relative_path)
    
    return sorted(image_files)  # Sort for consistent order

def generate_image_list():
    """Generate JSON file with list of all images"""
    content_dir = Path("content")
    output_file = Path("images.json")
    
    # Get all image files
    image_files = get_image_files_for_json(content_dir)
    
    if not image_files:
        print("No image files found in content folder!")
        return False
    
    # Create JSON structure
    image_data = {
        "images": image_files,
        "count": len(image_files),
        "last_updated": os.path.getmtime(content_dir)
    }
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(image_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated {output_file} with {len(image_files)} images:")
        for img in image_files:
            print(f"   - {img}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing {output_file}: {str(e)}")
        return False

def main():
    """Entry point - runs content organization first, then generates image list"""
    try:
        print("🔄 Starting content organization...")
        print("=" * 50)
        
        # Step 1: Organize content (from content_org.py)
        org_success = organize_content()
        
        if not org_success:
            print("\n❌ Content organization failed. Skipping image list generation.")
            return
        
        print("\n" + "=" * 50)
        print("🔍 Generating image list...")
        
        # Step 2: Generate image list (from generate_image_list.py)
        list_success = generate_image_list()
        
        print("\n" + "=" * 50)
        if org_success and list_success:
            print("✨ Content organization and image list generation completed successfully!")
            print("💡 Tip: Run this script whenever you add new images to the content folder.")
        else:
            print("⚠️ Some operations completed with issues. Please check the output above.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user.")
    except Exception as e:
        print(f"\n💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()