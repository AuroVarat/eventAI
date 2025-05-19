# bot_core.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from event_manager import add_event, get_all_events
from config import TELEGRAM_BOT_TOKEN # Import from config
import llm_handler # Import the llm_handler module
from datetime import datetime, timedelta

def create_ics_file(name, date, time, user_id, file_path="event.ics"):
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

    dt_end = dt + timedelta(hours=1)

    content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{name}
DTSTART:{dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}
DESCRIPTION:Created by Telegram user {user_id}
END:VEVENT
END:VCALENDAR
"""
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

# --- Logging Setup ---
# Configure logging once, here in the main entry point
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# You can also set higher logging levels for libraries like httpx if they are too verbose
# logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Telegram Bot Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm your event reminder bot. Send me details about an event!"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"Received message from chat_id {chat_id}: {user_message}")

    if not llm_handler.gemini_model: # Check if LLM was initialized
        await context.bot.send_message(chat_id=chat_id, text="Sorry, the event extraction service is currently unavailable.")
        return

    event_details = llm_handler.extract_event_details_with_llm(user_message)

    if event_details:
        if event_details.get("event_name") == "Parse Error":
            response_text = f"Sorry, I had trouble understanding the event details from the AI. Details: {event_details.get('place')}"
        elif "error" in event_details.get("event_name", "").lower(): # General error check
             response_text = f"Sorry, I encountered an error processing your request. Details: {event_details}"
        else:
            response_text = (
                f"Event Details:\n"
                f"Name: {event_details.get('event_name', 'Not specified')}\n"
                f"Place: {event_details.get('place', 'Not specified')}\n"
                f"Time: {event_details.get('time', 'Not specified')}\n\n"
                # f"✅ Event added successfully."
            )
            await context.bot.send_message(chat_id=chat_id, text=response_text)

            add_event(
                name = event_details.get("event_name", "Not specified"),
                date = event_details.get("time", "Not specified").split("T")[0], # Extract date part
                time = event_details.get("time", "Not specified").split("T")[1] if "T" in event_details.get("time", "Not specified") else None,
                location= event_details.get("place", "Not specified"),
                user_id = chat_id
            )
            logger.info(f"Event details stored for chat_id {chat_id}: {event_details}"
            )
            ics_path = create_ics_file(
            name=event_details.get("event_name", "Not specified"),
            date=event_details.get("time", "").split("T")[0],
            time=event_details.get("time", "").split("T")[1] if "T" in event_details.get("time", "") else "00:00",
            user_id=chat_id
            )
        
            await context.bot.send_document(
                chat_id=chat_id,
                document=open(ics_path, "rb"),
                filename="event.ics",
                caption="📅 Tap to add this event to your calendar."
            )

            # Placeholder for database storage:
            # store_event_in_db(event_details, chat_id)
            # logger.info(f"Event details ready for storage for chat_id {chat_id}: {event_details}")
    else:
        response_text = "Sorry, I couldn't extract any event details from your message or an unexpected error occurred."

        await context.bot.send_message(chat_id=chat_id, text=response_text)

def main():
    # Initialize the LLM once when the bot starts
    if not llm_handler.initialize_llm():
        logger.error("Failed to initialize LLM. Bot might not function as expected for event extraction.")
        # You could choose to exit or run with limited functionality
        # return

    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_FALLBACK' or not TELEGRAM_BOT_TOKEN:
        logger.error("CRITICAL: TELEGRAM_BOT_TOKEN is not configured. Please set the environment variable. Bot cannot start.")
        return

    logger.info("Building Telegram application...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    start_cmd_handler = CommandHandler('start', start_command)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler)

    application.add_handler(start_cmd_handler)
    application.add_handler(msg_handler)

    logger.info("Bot starting polling...")
    application.run_polling()

if __name__ == '__main__':
    main()