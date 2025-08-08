import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import threading

def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        config = json.load(f)[0]  # Take first element from the array
    return config

def create_browser_instance():
    """Create a new browser instance with Chrome in headless mode"""
    chrome_options = Options()
    # Run in headless mode
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def run_single_browser(min_delay, max_delay, instance_num):
    """Run a single browser instance"""
    try:
        print(f"Starting browser instance {instance_num + 1}")
        
        # Create browser instance
        driver = create_browser_instance()
        
        # Navigate to the website
        driver.get("https://deepabhabhi.github.io/")
        
        # Random delay between min and max
        delay = random.randint(min_delay, max_delay)
        print(f"Browser instance {instance_num + 1} will stay open for {delay} seconds")
        
        # Wait for the specified time
        time.sleep(delay)
        
        # Close the browser
        driver.quit()
        print(f"Browser instance {instance_num + 1} closed")
        
    except Exception as e:
        print(f"Error in browser instance {instance_num + 1}: {str(e)}")

def run_iteration(iteration_num, min_delay, max_delay):
    """Run one iteration with 5 browser windows"""
    print(f"\n--- Starting iteration {iteration_num + 1} ---")
    
    # Use ThreadPoolExecutor to run 5 browser instances simultaneously
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for i in range(5):
            future = executor.submit(run_single_browser, min_delay, max_delay, i)
            futures.append(future)
        
        # Wait for all browsers to complete
        for future in futures:
            future.result()
    
    print(f"--- Iteration {iteration_num + 1} completed ---")

def main():
    """Main function to orchestrate the bot"""
    try:
        # Load configuration
        config = load_config()
        total_messages = config['total_messages']
        min_delay = config['min_delay']
        max_delay = config['max_delay']
        
        print(f"Starting hit_bot with configuration:")
        print(f"Total iterations: {total_messages}")
        print(f"Delay range: {min_delay}-{max_delay} seconds")
        print(f"Browser instances per iteration: 5")
        print(f"Total browser instances: {total_messages * 5}")
        
        # Run iterations
        for i in range(total_messages):
            run_iteration(i, min_delay, max_delay)
            
            # Small delay between iterations to avoid overwhelming the system
            if i < total_messages - 1:  # Don't wait after the last iteration
                print(f"Waiting 5 seconds before next iteration...")
                time.sleep(5)
        
        print(f"\n🎉 All {total_messages} iterations completed successfully!")
        print(f"Total browser instances launched: {total_messages * 5}")
        
    except FileNotFoundError:
        print("Error: config.json file not found!")
    except KeyError as e:
        print(f"Error: Missing key in config.json: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()