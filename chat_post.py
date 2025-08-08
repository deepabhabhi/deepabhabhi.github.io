import time
import re
import json
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def is_running_in_ci():
    """Check if script is running in CI/CD environment"""
    ci_indicators = ['GITHUB_ACTIONS', 'CI', 'CONTINUOUS_INTEGRATION', 'BUILD_NUMBER', 'JENKINS_URL']
    return any(os.getenv(indicator) for indicator in ci_indicators)


def wait_for_user_input(message="Press Enter to continue..."):
    """Wait for user input only if not running in CI"""
    if is_running_in_ci():
        print(f"{message} (Skipped - running in CI environment)")
        return
    else:
        print(message)
        input()


def load_username():
    """Load username from username.json file"""
    with open('username.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        username = data['username']
        print(f"Loaded username: {username}")
        return username


def load_messages():
    """Load all messages from messages.json file"""
    with open('messages.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)
        print(f"Loaded {len(messages)} messages from messages.json")
        return messages


def get_random_message(messages):
    """Get a random message from the messages list"""
    selected_message = random.choice(messages)
    message = selected_message['message']
    print(f"Selected random message: {message}")
    return message


def load_config():
    """Load configuration from config.json file"""
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        config = config_data[0]  # Get the first config object
        total_messages = config['total_messages']
        min_delay = config['min_delay']
        max_delay = config['max_delay']
        print(f"Loaded config - Total messages: {total_messages}, Min delay: {min_delay}s, Max delay: {max_delay}s")
        return total_messages, min_delay, max_delay


def setup_advanced_adblocking():
    """Setup advanced ad blocking using Chrome arguments and host blocking"""
    print("Setting up advanced ad blocking with Chrome arguments...")
    
    # List of ad/tracking domains to block
    blocked_domains = [
        "doubleclick.net",
        "googleadservices.com",
        "googlesyndication.com",
        "googletagmanager.com",
        "googletagservices.com",
        "google-analytics.com",
        "adsystem.amazon.com",
        "amazon-adsystem.com",
        "facebook.com/tr",
        "connect.facebook.net",
        "ads.yahoo.com",
        "advertising.com",
        "adsymptotic.com",
        "outbrain.com",
        "taboola.com",
        "criteo.com",
        "pubmatic.com",
        "rubiconproject.com",
        "openx.net",
        "adsafeprotected.com"
    ]
    
    # Create host blocking rules
    host_rules = []
    for domain in blocked_domains:
        host_rules.append(f"MAP {domain} 127.0.0.1")
        host_rules.append(f"MAP *.{domain} 127.0.0.1")
    
    return host_rules


def setup_chrome_driver():
    """Setup Chrome driver with advanced ad blocking and optimizations"""
    print("Setting up Chrome driver...")
    
    chrome_options = Options()
    
    # Basic optimizations
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    
    # Run headless in CI environment
    if is_running_in_ci():
        chrome_options.add_argument("--headless")
        print("Running in headless mode for CI environment")
    
    # Ad blocking arguments
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Set default zoom level
    chrome_options.add_argument("--force-device-scale-factor=0.8")
    
    # Get host blocking rules
    host_rules = setup_advanced_adblocking()
    if host_rules:
        chrome_options.add_argument(f"--host-resolver-rules={','.join(host_rules)}")
    
    # Setup driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("Browser opened in headless mode")
    
    # Set zoom to 80% using CSS (headless compatible)
    try:
        driver.execute_script("document.body.style.zoom='0.8'")
        print("Browser zoom set to 80% using CSS")
    except Exception as e:
        print(f"CSS zoom failed: {e}")
    
    return driver


def wait_for_iframe_and_input(driver, username="sahil", max_wait_time=30):
    """Wait for iframe to load dynamically and find username input field"""
    print("Waiting for iframe to load dynamically...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check if any iframes are present
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                print(f"Found {len(iframes)} iframe(s) after {time.time() - start_time:.1f} seconds")
                
                for i, iframe in enumerate(iframes):
                    try:
                        print(f"Checking iframe {i+1}")
                        driver.switch_to.frame(iframe)
                        
                        # Wait a bit for iframe content to load
                        time.sleep(2)
                        
                        # Try to find input with dynamic ID using CSS selector pattern
                        input_selectors = [
                            "input[id^='inp_']",  # ID starts with 'inp_'
                            "input[type='text']",  # Fallback to text inputs
                            "input[name*='user']",  # Name contains 'user'
                            "input[placeholder*='user']",  # Placeholder contains 'user'
                            "form input[type='text']",  # Text inputs in forms
                            "div input[type='text']",  # Text inputs in divs
                        ]
                        
                        username_input = None
                        for selector in input_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if elements:
                                    print(f"Found {len(elements)} element(s) with selector: {selector}")
                                    for element in elements:
                                        try:
                                            element_id = element.get_attribute('id')
                                            element_name = element.get_attribute('name')
                                            element_placeholder = element.get_attribute('placeholder')
                                            element_class = element.get_attribute('class')
                                            print(f"Element - ID: {element_id}, Name: {element_name}, Placeholder: {element_placeholder}, Class: {element_class}")
                                            
                                            # Check if this looks like a username field
                                            if (element_id and element_id.startswith('inp_')) or \
                                               (element_name and 'user' in element_name.lower()) or \
                                               (element_placeholder and 'user' in element_placeholder.lower()) or \
                                               (element_class and 'user' in element_class.lower()):
                                                username_input = element
                                                break
                                        except Exception as e:
                                            print(f"Error checking element attributes: {e}")
                                            continue
                                    
                                    if username_input:
                                        break
                            except Exception as e:
                                print(f"Error with selector {selector}: {e}")
                                continue
                        
                        if username_input:
                            print(f"Found username input field with ID: {username_input.get_attribute('id')}")
                            
                            try:
                                # Wait for element to be clickable
                                WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable(username_input)
                                )
                                
                                # Clear and input username
                                username_input.clear()
                                username_input.send_keys(username)
                                print(f"Successfully entered username: {username}")
                                
                                # Press Enter to submit
                                username_input.send_keys(Keys.RETURN)
                                print("Pressed Enter to submit username")
                                
                                # Wait a moment for any response
                                time.sleep(2)
                                
                                # Switch back to main content
                                driver.switch_to.default_content()
                                return True
                            except Exception as e:
                                print(f"Error interacting with username input: {e}")
                                driver.switch_to.default_content()
                                continue
                        else:
                            print("Username input field not found in this iframe")
                            # Switch back to main content before trying next iframe
                            driver.switch_to.default_content()
                            
                    except Exception as e:
                        print(f"Error processing iframe {i+1}: {e}")
                        # Make sure to switch back to main content
                        try:
                            driver.switch_to.default_content()
                        except:
                            pass
                        continue
            else:
                print(f"No iframes found yet, waiting... ({time.time() - start_time:.1f}s)")
                time.sleep(2)  # Wait 2 seconds before checking again
                
        except Exception as e:
            print(f"Error while waiting for iframe: {e}")
            time.sleep(2)
    
    print(f"Timeout: No suitable iframe with username input found after {max_wait_time} seconds")
    return False


def find_username_input_in_iframe(driver, username="sahil"):
    """Find and fill username input field in iframe with dynamic ID"""
    print("Looking for iframe and username input field...")
    
    # First, wait for the iframe to load dynamically
    return wait_for_iframe_and_input(driver, username)


def send_chat_message(driver, message="hello everyone", wait_before=True):
    """Find the chat message input and send a message"""
    if wait_before:
        print(f"Waiting 30 seconds before looking for chat message input...")
        time.sleep(30)
    
    print("Looking for chat message input field...")
    
    try:
        # Try different selectors for the message input
        message_selectors = [
            "div[placeholder='Send a message...']",
            "[placeholder='Send a message...']",
            "div[contenteditable='true']",
            "textarea[placeholder*='message']",
            "input[placeholder*='message']",
            "div[role='textbox']",
            ".message-input",
            "#message-input"
        ]
        
        message_input = None
        
        # First try to find it in the main page
        for selector in message_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} element(s) with selector: {selector}")
                    for element in elements:
                        try:
                            placeholder = element.get_attribute('placeholder')
                            role = element.get_attribute('role')
                            contenteditable = element.get_attribute('contenteditable')
                            element_class = element.get_attribute('class')
                            element_id = element.get_attribute('id')
                            print(f"Element - Placeholder: {placeholder}, Role: {role}, Contenteditable: {contenteditable}, Class: {element_class}, ID: {element_id}")
                            
                            # Check if this looks like a message input
                            if (placeholder and 'message' in placeholder.lower()) or \
                               (role and role == 'textbox') or \
                               (contenteditable and contenteditable == 'true'):
                                message_input = element
                                break
                        except Exception as e:
                            print(f"Error checking element attributes: {e}")
                            continue
                    
                    if message_input:
                        break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If not found in main page, try in iframes
        if not message_input:
            print("Message input not found in main page, checking iframes...")
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Checking iframe {i+1} for message input")
                    driver.switch_to.frame(iframe)
                    
                    for selector in message_selectors:
                        try:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                print(f"Found {len(elements)} element(s) in iframe with selector: {selector}")
                                for element in elements:
                                    try:
                                        placeholder = element.get_attribute('placeholder')
                                        role = element.get_attribute('role')
                                        contenteditable = element.get_attribute('contenteditable')
                                        print(f"Iframe Element - Placeholder: {placeholder}, Role: {role}, Contenteditable: {contenteditable}")
                                        
                                        if (placeholder and 'message' in placeholder.lower()) or \
                                           (role and role == 'textbox') or \
                                           (contenteditable and contenteditable == 'true'):
                                            message_input = element
                                            break
                                    except Exception as e:
                                        print(f"Error checking iframe element attributes: {e}")
                                        continue
                                
                                if message_input:
                                    break
                        except Exception as e:
                            print(f"Error with selector {selector} in iframe: {e}")
                            continue
                    
                    if message_input:
                        print(f"Found message input in iframe {i+1}")
                        break
                    else:
                        driver.switch_to.default_content()
                        
                except Exception as e:
                    print(f"Error processing iframe {i+1} for message input: {e}")
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass
                    continue
        
        if message_input:
            try:
                print(f"Found message input field, sending message: {message}")
                
                # Wait for element to be clickable
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(message_input)
                )
                
                # Click on the message input
                message_input.click()
                print("Clicked on message input field")
                
                # Clear any existing text and type the message
                message_input.clear()
                message_input.send_keys(message)
                print(f"Typed message: {message}")
                
                # Press Enter to send
                message_input.send_keys(Keys.RETURN)
                print("Pressed Enter to send message")
                
                # Switch back to main content if we were in an iframe
                driver.switch_to.default_content()
                
                return True
                
            except Exception as e:
                print(f"Error sending message: {e}")
                driver.switch_to.default_content()
                return False
        else:
            print("Message input field not found")
            return False
            
    except Exception as e:
        print(f"Error finding message input: {e}")
        return False


def send_multiple_messages(driver, messages, total_messages, min_delay, max_delay):
    """Send multiple messages with random delays"""
    print(f"Starting to send {total_messages} messages with delays between {min_delay}-{max_delay} seconds")
    
    # Send the first message immediately (after the initial 30-second wait)
    first_message = get_random_message(messages)
    success = send_chat_message(driver, first_message, wait_before=True)
    
    if not success:
        print("Failed to send first message, aborting...")
        return False
    
    messages_sent = 1
    print(f"Message {messages_sent}/{total_messages} sent successfully")
    
    # Send remaining messages with random delays
    for i in range(1, total_messages):
        # Calculate random delay
        delay = random.uniform(min_delay, max_delay)
        print(f"Waiting {delay:.1f} seconds before sending next message...")
        time.sleep(delay)
        
        # Get a random message
        message = get_random_message(messages)
        
        # Send the message (without the initial 30-second wait)
        success = send_chat_message(driver, message, wait_before=False)
        
        if success:
            messages_sent += 1
            print(f"Message {messages_sent}/{total_messages} sent successfully")
        else:
            print(f"Failed to send message {i+1}, continuing...")
    
    print(f"Completed sending messages. Total sent: {messages_sent}/{total_messages}")
    return messages_sent > 0


def navigate_and_input_username():
    """Main function to navigate to the website and input username"""
    driver = None
    try:
        # Load configuration and data from JSON files
        username = load_username()
        messages = load_messages()
        total_messages, min_delay, max_delay = load_config()
        
        # Setup driver
        driver = setup_chrome_driver()
        
        # Navigate to website
        print("Navigating to https://www.allindiachat.com/")
        driver.get("https://www.allindiachat.com/")
        
        # Wait for initial page to load
        print("Waiting for initial page to load...")
        time.sleep(5)
        
        # Wait for page to be ready
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page loaded completely")
        
        # Find and fill username input in iframe (this will wait for iframe to load dynamically)
        success = find_username_input_in_iframe(driver, username)
        
        if success:
            print("Successfully completed username input!")
            
            # Now send multiple chat messages with random delays
            message_success = send_multiple_messages(driver, messages, total_messages, min_delay, max_delay)
            
            if message_success:
                print("Successfully completed sending all messages!")
            else:
                print("Failed to send messages")
                
            wait_for_user_input("Browser will remain open. Press Enter in this console to close the browser...")
        else:
            print("Failed to input username")
            wait_for_user_input("Browser will remain open. Press Enter in this console to close the browser...")
            
    except Exception as e:
        print(f"Error in main function: {e}")
        if driver:
            wait_for_user_input("Browser will remain open. Press Enter in this console to close the browser...")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    navigate_and_input_username()