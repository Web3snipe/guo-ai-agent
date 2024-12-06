import sys
import os

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from agent import GuoTwitterAgent

def main():
    agent = GuoTwitterAgent()
    agent.run()

if __name__ == "__main__":
    main()