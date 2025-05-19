#  eventAI

eventAI is a bot that helps users manage tasks and schedule events effortlessly. Powered by AI, it extracts event details from natural language messages, generates `.ics` calendar files, and integrates seamlessly with calendar apps.

## Message Support
Only on Telegram at the moment. I would ideally like to add support for other messaging platforms like WhatsApp, Discord, etc. in the future.

## Features
- Extracts event details (name, time, location) from user messages using AI.
- Automatically generates `.ics` calendar files for easy calendar integration.
- Sends event details and calendar files directly to users via Telegram.
- Simple and intuitive interface for task and event management.

## Installation
1. Clone the repository:

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Telegram bot token and Gemini API key in a `config.py` file or in your environment variables.


## Usage
1. Run the bot:
   ```bash
   python bot_core.py
   ```

2. Interact with the bot on Telegram to create and manage events.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.