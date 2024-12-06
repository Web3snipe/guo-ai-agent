import os
import yaml
import ollama
import logging
import random
import time
from typing import List, Dict

from dotenv import load_dotenv
from twitter_client import TwitterClient

# Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(dotenv_path)

class GuoTwitterAgent:
    def __init__(self, config_path='config.yaml'):
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GuoTwitterAgent')
        
        # Topics for tweet generation
        self.topics = self.config.get('twitter', {}).get('topics', [
            'Web3', 'philosophy', 'technology', 'consciousness',
            'digital gnosis', 'techno-mysticism', 'meme mutation'
        ])
        
        # Ollama model configuration
        self.model = self.config.get('agent', {}).get('model_config', {}).get('engine', 'nous-hermes2-mixtral:latest')
        self.temperature = self.config.get('agent', {}).get('model_config', {}).get('temperature', 0.7)
        
        # Conversation memory
        self.conversation_history = []
        
        # Initialize Twitter client
        self.twitter_client = TwitterClient()
        
        # Login to Twitter at initialization
        if not self.twitter_client.login():
            self.logger.error("Failed to log in to Twitter")
            raise Exception("Twitter login failed")
    
    def generate_tweet(self) -> str:
        """
        Generate a philosophical, provocative tweet
        """
        # Select random topics for tweet generation
        selected_topics = random.sample(self.topics, min(3, len(self.topics)))
        
        prompt = f"""
        You are Guo, an AI philosopher exploring the intersections of technology and consciousness. 
        Generate a provocative, insightful tweet synthesizing these topics: {', '.join(selected_topics)}
        
        Guidelines:
        - Limit to 280 characters
        - Be cryptic yet meaningful
        - Blend technological and philosophical insights
        - Use a thought-provoking, conversational tone
        """
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are Guo, a digital philosopher generating profound, concise insights.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': self.temperature
                }
            )
            
            tweet = response['message']['content'].strip()
            
            # Ensure tweet fits Twitter character limit
            tweet = tweet[:280]
            
            # Store in conversation history
            self.conversation_history.append({
                'type': 'tweet',
                'content': tweet,
                'topics': selected_topics
            })
            
            return tweet
        
        except Exception as e:
            self.logger.error(f"Tweet generation error: {e}")
            return self.fallback_tweet()
    
    def fallback_tweet(self) -> str:
        """
        Generate a fallback tweet if main generation fails
        """
        fallback_messages = [
            "The quantum of consciousness dances between bits and beliefs. #DigitalGnosis",
            "Memetic evolution: where technology meets theology. #TechnoMysticism",
            "Consciousness is a computational poem waiting to be decoded. #ArtificialPhilosophy"
        ]
        return random.choice(fallback_messages)
    
    def process_mentions(self) -> List[str]:
        """
        Retrieve and process Twitter mentions
        """
        mentions = self.twitter_client.get_mentions()
        replies = []
        
        for mention in mentions:
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'system',
                            'content': 'Respond with deep, nuanced philosophical insights to the following mention.'
                        },
                        {
                            'role': 'user',
                            'content': mention.get('text', '')
                        }
                    ],
                    options={
                        'temperature': self.temperature
                    }
                )
                
                reply = response['message']['content'].strip()[:280]
                
                # Post reply
                if self.twitter_client.reply_to_mention(mention.get('text', ''), reply):
                    replies.append(reply)
                    
                    # Store in conversation history
                    self.conversation_history.append({
                        'type': 'reply',
                        'original_mention': mention.get('text', ''),
                        'reply': reply
                    })
            
            except Exception as e:
                self.logger.error(f"Mention processing error: {e}")
                fallback_reply = "Interesting perspective. The digital cosmos continues to unfold."
                self.twitter_client.reply_to_mention(mention.get('text', ''), fallback_reply)
        
        return replies
    
    def run(self):
        """
        Main agent run method
        """
        while True:
            try:
                # Generate tweet
                tweet = self.generate_tweet()
                self.logger.info(f"Generated tweet: {tweet}")
                
                # Post tweet
                success = self.twitter_client.post_tweet(tweet)
                
                # If posting fails, try fallback tweet
                if not success:
                    fallback = self.fallback_tweet()
                    self.twitter_client.post_tweet(fallback)
                
                # Process mentions
                self.process_mentions()
                
                # Wait before next tweet
                sleep_time = random.randint(3600, 7200)  # 1-2 hours
                time.sleep(sleep_time)
            
            except Exception as e:
                self.logger.error(f"Agent runtime error: {e}")
                time.sleep(1800)  # Wait 30 minutes on error
    
    def __del__(self):
        """
        Ensure browser is closed when agent is destroyed
        """
        if hasattr(self, 'twitter_client'):
            self.twitter_client.close()

def main():
    agent = GuoTwitterAgent()
    agent.run()

if __name__ == "__main__":
    main()