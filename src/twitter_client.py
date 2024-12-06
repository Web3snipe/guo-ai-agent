import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

class TwitterClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Twitter credentials
        self.username = os.getenv('TWITTER_USERNAME')
        self.password = os.getenv('TWITTER_PASSWORD')
        
        # Webdriver setup
        self.driver = self._setup_webdriver()
        
    def _setup_webdriver(self):
        """
        Setup Chrome webdriver with options
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Uncomment for headless mode
        # options.add_argument('--headless')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    
    def login(self):
        """
        Login to Twitter
        """
        try:
            self.driver.get('https://twitter.com/login')
            time.sleep(3)
            
            # Find username input
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'text'))
            )
            username_input.send_keys(self.username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Find password input
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'password'))
            )
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            
            # Wait for login
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('home')
            )
            
            self.logger.info("Successfully logged in to Twitter")
            return True
        
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def post_tweet(self, tweet_text):
        """
        Post a tweet
        """
        try:
            # Navigate to tweet composition
            tweet_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='SideNav-NewTweet-Button']"))
            )
            tweet_button.click()
            time.sleep(2)
            
            # Find tweet input
            tweet_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea-0']"))
            )
            tweet_input.send_keys(tweet_text)
            time.sleep(1)
            
            # Post tweet
            post_button = self.driver.find_element(By.XPATH, "//button[@data-testid='tweetButtonInner']")
            post_button.click()
            
            self.logger.info(f"Tweet posted: {tweet_text}")
            time.sleep(3)
            return True
        
        except Exception as e:
            self.logger.error(f"Tweet posting failed: {e}")
            return False
    
    def get_mentions(self):
        """
        Retrieve recent mentions
        """
        try:
            self.driver.get('https://twitter.com/notifications/mentions')
            time.sleep(3)
            
            # Find mention elements
            mentions = self.driver.find_elements(By.XPATH, "//div[@data-testid='tweet']")
            
            parsed_mentions = []
            for mention in mentions[:10]:  # Limit to 10 recent mentions
                try:
                    # Extract tweet text
                    tweet_text = mention.find_element(By.XPATH, ".//div[@lang]").text
                    parsed_mentions.append({
                        'text': tweet_text
                    })
                except Exception as inner_e:
                    self.logger.warning(f"Could not parse mention: {inner_e}")
            
            return parsed_mentions
        
        except Exception as e:
            self.logger.error(f"Retrieving mentions failed: {e}")
            return []
    
    def reply_to_mention(self, mention_text, reply_text):
        """
        Reply to a specific mention
        """
        try:
            # Find reply button for the specific mention
            reply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{mention_text[:20]}')]//following::button[@data-testid='replyButton']"))
            )
            reply_button.click()
            time.sleep(2)
            
            # Find reply input
            reply_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea-0']"))
            )
            reply_input.send_keys(reply_text)
            time.sleep(1)
            
            # Post reply
            post_reply_button = self.driver.find_element(By.XPATH, "//button[@data-testid='tweetButtonInner']")
            post_reply_button.click()
            
            self.logger.info(f"Replied to mention: {reply_text}")
            time.sleep(3)
            return True
        
        except Exception as e:
            self.logger.error(f"Replying to mention failed: {e}")
            return False
    
    def close(self):
        """
        Close the browser
        """
        if self.driver:
            self.driver.quit()