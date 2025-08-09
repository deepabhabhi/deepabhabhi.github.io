#!/usr/bin/env python3
"""
Content Downloader - Extracts image download links from massagerepublic.com
"""

import re
import time
import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def click_entry_button(driver):
    """Click the 'YES - Enter' button if present"""
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Try CSS selector first
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary.btn-lg.fw-bold.px-4"))
            )
            print("Found button using CSS selector, clicking...")
            button.click()
            time.sleep(3)  # Wait for page to load after click
            return True
        except TimeoutException:
            pass
        
        # Try XPath as fallback
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='YES - Enter']"))
            )
            print("Found button using XPath, clicking...")
            button.click()
            time.sleep(3)  # Wait for page to load after click
            return True
        except TimeoutException:
            pass
            
        print("No entry button found, proceeding...")
        return False
        
    except Exception as e:
        print(f"Error while looking for entry button: {e}")
        return False


def extract_image_links(driver):
    """Extract image download links that match the specified pattern"""
    image_links = []
    
    try:
        # Wait for images to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )
        
        # Find all images on the page
        images = driver.find_elements(By.TAG_NAME, "img")
        
        # Pattern to match alt text like: "Delhi Escorts 5★star Luxury Hotels VIP - escort in New Delhi Photo 1 of 8"
        # or "Ruhi real meet/cam - escort in New Delhi Photo 1 of 6"
        alt_pattern = re.compile(r'.*- escort in New Delhi Photo \d+ of \d+.*', re.IGNORECASE)
        
        print(f"Found {len(images)} images on the page")
        
        for img in images:
            try:
                alt_text = img.get_attribute('alt')
                src = img.get_attribute('src')
                
                if alt_text and alt_pattern.match(alt_text):
                    if src:
                        # Replace _premium.jpg and _mini.jpg with _original.jpg
                        original_url = src.replace('_premium.jpg', '_original.jpg').replace('_mini.jpg', '_original.jpg')
                        
                        print(f"Match found - Alt: {alt_text}")
                        print(f"Original URL: {src}")
                        print(f"Modified URL: {original_url}")
                        image_links.append({
                            'alt': alt_text,
                            'url': original_url,
                            'original_url': src
                        })
                        print("-" * 80)
                        
            except Exception as e:
                print(f"Error processing image: {e}")
                continue
    
    except Exception as e:
        print(f"Error while extracting images: {e}")
    
    return image_links


def create_content_folder():
    """Create content folder if it doesn't exist"""
    content_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content')
    if not os.path.exists(content_folder):
        os.makedirs(content_folder)
        print(f"Created content folder: {content_folder}")
    else:
        print(f"Content folder already exists: {content_folder}")
    return content_folder


def get_unique_filename(folder, filename):
    """Get a unique filename by adding numbers if file already exists"""
    base_path = os.path.join(folder, filename)
    if not os.path.exists(base_path):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(folder, new_filename)
        if not os.path.exists(new_path):
            return new_filename
        counter += 1


def download_image(url, folder, filename):
    """Download an image from URL and save to folder"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Get unique filename
        unique_filename = get_unique_filename(folder, filename)
        file_path = os.path.join(folder, unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {unique_filename} ({len(response.content)} bytes)")
        return True, unique_filename
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return False, None
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False, None


def download_all_images(image_links, content_folder):
    """Download all images from the list"""
    downloaded_count = 0
    failed_count = 0
    
    print(f"\nStarting download of {len(image_links)} images to: {content_folder}")
    print("=" * 80)
    
    for i, img_data in enumerate(image_links, 1):
        url = img_data['url']
        
        # Generate filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
            filename = f"image_{i}.jpg"
        
        print(f"[{i}/{len(image_links)}] Downloading: {filename}")
        print(f"URL: {url}")
        
        success, saved_filename = download_image(url, content_folder, filename)
        
        if success:
            downloaded_count += 1
            print(f"✓ Saved as: {saved_filename}")
        else:
            failed_count += 1
            print(f"✗ Failed to download")
        
        print("-" * 40)
        
        # Small delay between downloads
        time.sleep(1)
    
    print("\nDownload Summary:")
    print(f"Successfully downloaded: {downloaded_count}")
    print(f"Failed downloads: {failed_count}")
    print(f"Total processed: {len(image_links)}")


def main():
    """Main function to run the content downloader"""
    url = "https://massagerepublic.com/female-escorts-in-new-delhi"
    driver = None
    
    try:
        print(f"Starting content downloader for: {url}")
        print("=" * 80)
        
        # Create content folder
        content_folder = create_content_folder()
        
        # Setup driver
        driver = setup_driver()
        
        # Open the URL
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Click entry button if present
        click_entry_button(driver)
        
        # Extract image links
        print("Extracting image download links...")
        image_links = extract_image_links(driver)
        
        # Print results
        print("\n" + "=" * 80)
        print("EXTRACTION RESULTS:")
        print("=" * 80)
        
        if image_links:
            print(f"Found {len(image_links)} matching images:")
            print("\nAll Modified Image Download Links:")
            print("-" * 40)
            
            for i, img_data in enumerate(image_links, 1):
                print(f"{i}. {img_data['url']}")
            
            print("\nDetailed Information:")
            print("-" * 40)
            for i, img_data in enumerate(image_links, 1):
                print(f"{i}. Alt Text: {img_data['alt']}")
                print(f"   Original URL: {img_data['original_url']}")
                print(f"   Modified URL: {img_data['url']}")
                print()
            
            # Download all images
            download_all_images(image_links, content_folder)
            
        else:
            print("No matching images found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()