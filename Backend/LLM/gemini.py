import google.generativeai as genai
import os
import logging
from .config import GEMINI_API_KEY

# Load the API Key from environment variables
api_key = GEMINI_API_KEY
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in the environment variables")

# Configure the Gemini API with the loaded API key
genai.configure(api_key=api_key)

# Logging setup
logging.basicConfig(
    filename='llm_post_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_content(self, prompt):
        """
        Generate content based on the provided prompt.

        :param prompt: The text prompt to send to the model.
        :return: The generated content.
        """
        try:
            response = self.model.generate_content(prompt)
            logger.info("Content generated successfully.")
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None

    def load_prompt(self, prompt_file):
        """
        Load a prompt from a text file.

        :param prompt_file: The path to the prompt file.
        :return: The prompt text.
        """
        try:
            with open(prompt_file, 'r') as file:
                prompt = file.read().strip()  # Read and strip any extra whitespace
            logger.info(f"Loaded prompt from {prompt_file}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to load prompt from {prompt_file}: {e}")
            return None

def main():
    """
    Main function to read the selected deal, generate LinkedIn post content, and save the result.
    """
    client = GeminiClient()

    # Load prompt from file
    prompt_path = os.path.join('Backend', 'LLM', 'prompts', 'magic_backpack_prompt.txt')  # Adjust path as necessary
    prompt = client.load_prompt(prompt_path)

    if prompt:
        generated_content = client.generate_content(prompt)
        if generated_content:
            print(generated_content)
        else:
            print("Failed to generate content.")
    else:
        print("Prompt loading failed.")

if __name__ == "__main__":
    main()
