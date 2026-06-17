from groq import Groq
import google.generativeai as genai
import os

# ======================
# Groq Setup
# ======================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ======================
# Gemini Setup
# ======================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ======================
# AI Fallback System
# ======================

def get_ai_response(user_message):
    try:
        print("🚀 Using Groq")

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return completion.choices[0].message.content

    except Exception as groq_error:
        print("❌ Groq Failed:", groq_error)

        try:
            print("🧠 Switching to Gemini")

            response = gemini_model.generate_content(
                user_message
            )

            return response.text

        except Exception as gemini_error:
            print("❌ Gemini Failed:", gemini_error)

            return (
                "⚠️ JARVIS AI is currently "
                "experiencing high traffic. "
                "Please try again in a few moments."
            )