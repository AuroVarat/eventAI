# config.py
import os

# Best practice: Load sensitive keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_FALLBACK')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_FALLBACK')

# You can also define model names or other settings here if needed
GEMINI_MODEL_NAME = "gemini-1.5-flash-8b" # Or "gemini-1.5-flash-latest", "gemini-1.5-flash-8b" etc.

# Fallback values are provided for clarity, but you should ensure your environment variables are set.
if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_FALLBACK':
    print("Warning: TELEGRAM_BOT_TOKEN is using a fallback value. Please set the environment variable.")

if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_FALLBACK':
    print("Warning: GEMINI_API_KEY is using a fallback value. Please set the environment variable.")