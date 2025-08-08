#!/usr/bin/env python3
"""
Generate Image List Script
Creates a JSON file with all images in the content folder
for dynamic loading in the web interface.
"""

import os
import json
from pathlib import Path

def get_image_files(content_dir):
    """Get all image files from the content directory"""
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
    image_files = get_image_files(content_dir)
    
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
    """Entry point"""
    try:
        print("🔍 Scanning content folder for images...")
        success = generate_image_list()
        
        if success:
            print("\n✨ Image list generated successfully!")
            print("💡 Tip: Run this script whenever you add new images to the content folder.")
        else:
            print("\n❌ Failed to generate image list.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user.")
    except Exception as e:
        print(f"\n💥 An error occurred: {str(e)}")

if __name__ == "__main__":
    main()