#!/usr/bin/env python3
"""
Content Organization Script
Converts all image files in the content folder to WebP format
and renames them sequentially as image_1.webp, image_2.webp, etc.
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import tempfile

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
        return
    
    # Get all image files
    image_files = []
    for file_path in content_dir.iterdir():
        if file_path.is_file() and is_image_file(file_path):
            image_files.append(file_path)
    
    if not image_files:
        print("No image files found in content folder!")
        return
    
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

def main():
    """Entry point"""
    try:
        organize_content()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()