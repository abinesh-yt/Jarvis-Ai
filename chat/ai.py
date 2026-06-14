from groq import Groq
from django.conf import settings
import os


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def get_ai_response(user_message):

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return completion.choices[0].message.content