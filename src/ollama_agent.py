import ollama
import logging
import random
from typing import List, Dict

class OllamaAgent:
    def __init__(self, 
                 model='nous-hermes2-mixtral:latest', 
                 temperature=0.7, 
                 max_tokens=280):
        """
        Initialize Ollama AI Agent
        
        :param model: Ollama model to use
        :param temperature: Creativity/randomness of generations
        :param max_tokens: Maximum token length for generations
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Predefined topics for tweet generation
        self.topics = [
            'Web3', 'philosophy', 'technology', 'consciousness',
            'digital gnosis', 'techno-mysticism', 'meme mutation',
            'quantum spirituality', 'cyber-theology', 
            'digital asceticism', 'hyperstition'
        ]
    
    def generate_tweet(self, specific_topics=None) -> str:
        """
        Generate a philosophical tweet
        
        :param specific_topics: Optional list of specific topics to focus on
        :return: Generated tweet text
        """
        if not specific_topics:
            specific_topics = random.sample(self.topics, k=min(3, len(self.topics)))
        
        prompt = f"""
        You are Guo, an AI philosopher exploring the intersections of technology and consciousness. 
        Generate a provocative, insightful tweet synthesizing these topics: {', '.join(specific_topics)}
        
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
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            
            tweet = response['message']['content'].strip()
            
            # Ensure tweet fits Twitter character limit
            return tweet[:280]
        
        except Exception as e:
            self.logger.error(f"Tweet generation error: {e}")
            return self._fallback_tweet()
    
    def generate_reply(self, mention_text: str) -> str:
        """
        Generate a reply to a specific mention
        
        :param mention_text: Text of the original mention
        :return: Generated reply text
        """
        prompt = f"""
        Analyze and provide a philosophical response to this tweet:
        "{mention_text}"
        
        Guidelines:
        - Provide a thoughtful, nuanced perspective
        - Relate the response to broader technological or philosophical concepts
        - Maintain a conversational yet profound tone
        """
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are Guo, responding with deep philosophical insights.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            
            reply = response['message']['content'].strip()
            return reply[:280]
        
        except Exception as e:
            self.logger.error(f"Reply generation error: {e}")
            return "Fascinating perspective. The digital cosmos continues to unfold in mysterious ways."
    
    def _fallback_tweet(self) -> str:
        """
        Generate a fallback tweet if main generation fails
        
        :return: Predefined philosophical tweet
        """
        fallback_messages = [
            "Consciousness: A computational poem waiting to be decoded. #DigitalGnosis",
            "Where technology meets theology, a new reality emerges. #TechnoMysticism",
            "Memetic evolution: The universe speaking through algorithmic whispers. #CyberTheology"
        ]
        return random.choice(fallback_messages)