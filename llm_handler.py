# llm_handler.py
import logging
import json
from datetime import datetime # Import datetime
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)
gemini_model = None

def initialize_llm():
    global gemini_model
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_FALLBACK':
        logger.error("GEMINI_API_KEY not configured properly. LLM will not be available.")
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        logger.info(f"Gemini model '{GEMINI_MODEL_NAME}' initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {e}")
        gemini_model = None
        return False

def extract_event_details_with_llm(message_text):
    if not gemini_model:
        logger.error("Gemini model not initialized. Cannot extract event details.")
        return None

    # Get current date and time to provide context to the LLM
    # Using ISO format for the current time passed to the LLM for clarity
    current_time_iso = datetime.now().isoformat(sep='T', timespec='seconds')
    # We can also provide the day of the week for better relative understanding.
    current_day_of_week = datetime.now().strftime('%A')


    # Updated prompt
    prompt = f"""
    You are an expert event detail extractor.
    Your task is to extract the event name, place, and time from the user's text.
    The current date and time is: {current_time_iso} (It is a {current_day_of_week}).
    Please use this current date and time to resolve any relative time references like "tomorrow", "next Tuesday", "tonight", "in 2 hours", "this evening at 7", etc.

    Return the information as a JSON object with the following keys:
    1.  "event_name": (string) The main activity or purpose of the event.
    2.  "place": (string) The location of the event.
    3.  "time": (string) The specific start date and time of the event in STRICT ISO 8601 format: "YYYY-MM-DDTHH:MM:SS".

    Guidelines for the "time" field:
    - If a full date and time are specified (e.g., "May 21st at 3 PM", "next Wednesday at 15:00"), convert it to "YYYY-MM-DDTHH:MM:SS". Assume the current year if not specified, unless the context implies otherwise (e.g. "January 10th" when current month is December usually means next year).
    - If only a date is specified (e.g., "tomorrow", "June 10th"), try to infer a common time if appropriate (e.g., morning for general day events if no other context) or use a default like "09:00:00" or "12:00:00". If no time can be reasonably inferred, use "00:00:00" for the time part on that date: "YYYY-MM-DDTHH:00:00:00".
    - If only a time is specified (e.g., "at 7 PM", "19:00"), assume it's for the current day ({current_time_iso[:10]}) if the time is in the future today. If the time mentioned is in the past for today, assume it's for tomorrow.
    - "Tonight" or "this evening" refers to the evening of the current date.
    - "Tomorrow morning/afternoon/evening" refers to the respective part of tomorrow's date.
    - If the time is vague (e.g., "sometime next week", "later"), set "time" to "Not specified".
    - If any component (year, month, day, hour, minute) cannot be determined for a specific time, set "time" to "Not specified". Do not guess components wildly.

    If any other field ("event_name", "place") is not clearly stated, use "Not specified" for its value.

    User Text: "{message_text}"

    JSON Output:
    """

    try:
        logger.info(f"Sending prompt to Gemini (current time context: {current_time_iso}): '{message_text[:50]}...'")
        response = gemini_model.generate_content(prompt)

        if response.parts:
            extracted_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif hasattr(response, 'text'):
            extracted_text = response.text
        else:
            logger.warning(f"Unexpected Gemini response structure: {response}")
            extracted_text = str(response)

        logger.info(f"Raw response from Gemini: {extracted_text}")

        json_str = extracted_text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.startswith("```"):
            json_str = json_str[len("```"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-len("```")].strip()

        try:
            event_data = json.loads(json_str)
            # Validate if the time field, if not "Not specified", looks like an ISO format (basic check)
            time_val = event_data.get("time")
            if time_val and time_val != "Not specified":
                try:
                    # Attempt to parse to validate format. This doesn't mean the date/time itself is correct, just the format.
                    datetime.fromisoformat(time_val.replace("Z", "")) # Replace Z if present, as fromisoformat might not handle it directly for naive datetimes
                    logger.info(f"Time field '{time_val}' appears to be valid ISO format.")
                except ValueError:
                    logger.warning(f"Time field '{time_val}' is NOT in expected ISO format. LLM might need prompt adjustment.")
                    # You might want to mark this as an error or try to re-parse/fix if possible
                    # For now, we'll accept it but log a warning.
                    # event_data["time_format_warning"] = "Time not in expected ISO YYYY-MM-DDTHH:MM:SS format"

            # Basic validation for expected keys
            if all(key in event_data for key in ["event_name", "place", "time"]):
                return event_data
            else:
                logger.warning(f"Extracted JSON missing expected keys: {json_str}")
                return event_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}. Response was: '{json_str}'")
            return {"event_name": "Parse Error", "place": f"Invalid JSON: {json_str[:100]}...", "time": "Parse Error"}

    except Exception as e:
        logger.error(f"Error calling Gemini API or processing response: {e}")
        return None