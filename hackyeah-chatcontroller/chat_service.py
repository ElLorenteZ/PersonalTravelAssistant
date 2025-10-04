import os
from openai import OpenAI

class ChatService:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))

    def send_prompt(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """
        Send a prompt to OpenAI chat model and return the response.

        Args:
            prompt: The user's message/prompt
            model: The OpenAI model to use (default: gpt-4o-mini)

        Returns:
            String response from the model
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
