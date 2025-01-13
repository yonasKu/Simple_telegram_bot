import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# List of fixed prefixes
PREFIXES = [
    "Your Highness",
    "The Genius King",
    "The Best of the Best",
    "Oh Magnificent",
    "The Supreme Leader",
    "The Noble Ruler"
]

# Dictionary to track users waiting for a response, and their message history
waiting_users = {}

# Custom response logic based on the prefix
def generate_response(prefix: str, user_message: str, message_history: list) -> str:
    # Some example logic to make responses dynamic based on history
    if prefix == "Your Highness":
        if "thank you" in user_message.lower():
            return "Your Highness, you are most welcome!"
        elif len(message_history) > 1:
            return f"Your Highness, you have been a true leader in your previous messages!"
        return "The King acknowledges your greatness!"
    
    elif prefix == "The Genius King":
        if "wisdom" in user_message.lower():
            return "Your Genius, your wisdom is unmatched!"
        elif len(message_history) > 2:
            return "Your Genius, I remember your profound thoughts from earlier!"
        return "The King is pleased with your brilliance!"
    
    elif prefix == "The Best of the Best":
        if "best" in user_message.lower():
            return "Indeed, you are the best of the best!"
        elif len(message_history) > 3:
            return "You truly are the best, and your message history proves it!"
        return "You are truly unparalleled!"
    
    elif prefix == "Oh Magnificent":
        if "mighty" in user_message.lower():
            return "Oh Magnificent One, your might is unrivaled!"
        elif len(message_history) > 1:
            return "Your magnificence shines even brighter with each message!"
        return "Your magnificence shines brightly!"
    
    elif prefix == "The Supreme Leader":
        if "order" in user_message.lower():
            return "The Supreme Leader commands with authority!"
        elif len(message_history) > 2:
            return "The Supreme Leader's guidance has been unwavering!"
        return "Your leadership is unquestionable, Supreme One!"
    
    elif prefix == "The Noble Ruler":
        if "honor" in user_message.lower():
            return "The Noble Ruler, your honor is a beacon to all!"
        elif len(message_history) > 1:
            return "Your nobility has inspired all, Ruler!"
        return "Your nobility is unmatched, Ruler!"

    # Default response if no specific conditions match
    return "Your Highness, your wish is my command!"

# Command: Start the bot with a welcome message
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create the prefix keyboard
    keyboard = [[prefix] for prefix in PREFIXES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Send a welcome message and prompt for prefix selection
    await update.message.reply_text(
        "Welcome to the Royal Bot! Please choose a title to start your message. Select one of the prefixes below:",
        reply_markup=reply_markup
    )

# Command: Show the prefix selection keyboard
async def prefixes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create the prefix keyboard
    keyboard = [[prefix] for prefix in PREFIXES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "Please select a title to start your message:",
        reply_markup=reply_markup
    )

# Handle prefix selection
async def handle_prefix_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_prefix = update.message.text

    # Validate if the selected text is a valid prefix (case-insensitive match)
    valid_prefix = next((p for p in PREFIXES if p.lower() == selected_prefix.lower()), None)
    if not valid_prefix:
        await update.message.reply_text(
            "Invalid selection. Please use /prefixes to choose a valid title.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Save the user ID and the selected prefix
    waiting_users[update.message.chat.id] = {
        "prefix": valid_prefix,
        "history": []  # Initialize history list
    }

    # Inform the user to type the rest of their message
    await update.message.reply_text(
        f"I'm waiting for your response starting with '{valid_prefix}'. Please type your comment.",
        reply_markup=ReplyKeyboardRemove()  # Remove the keyboard after selection
    )

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text.strip()

    # Check if the user is in the "waiting" state (meaning they selected a prefix)
    if user_id in waiting_users:
        selected_prefix = waiting_users[user_id]["prefix"]
        message_history = waiting_users[user_id]["history"]

        # Check if the message starts with the selected prefix (case-insensitive)
        if not text.lower().startswith(selected_prefix.lower()):
            await update.message.reply_text(
                f"Please start your message with '{selected_prefix}'. If you want to change your title, use /prefixes to choose a new one."
            )
            return

        # Add the user's message to the history
        message_history.append(text)

        # Generate a custom response based on the selected prefix, user message, and history
        response = generate_response(selected_prefix, text, message_history)
        formatted_response = f"{selected_prefix}, {response}"

        print(f"User: {text}\nBot: {formatted_response}")
        await update.message.reply_text(formatted_response)

        # Store the updated message history
        waiting_users[user_id]["history"] = message_history
    else:
        # If the user didn't select a prefix and just typed a message, reject it
        valid_prefix = next((p for p in PREFIXES if text.lower().startswith(p.lower())), None)
        if valid_prefix:
            # If the message manually starts with a valid prefix, process it
            response = generate_response(valid_prefix, text, [])
            formatted_response = f"{valid_prefix}, {response}"

            print(f"User: {text}\nBot: {formatted_response}")
            await update.message.reply_text(formatted_response)
        else:
            # If no valid prefix is detected, inform the user to use /prefixes and automatically guide them
            await update.message.reply_text(
                "I didn't understand that. Please use /prefixes to choose a valid title or start your message with one of the following prefixes:\n" + "\n".join(PREFIXES)
            )

# Handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Add handlers for commands
    app.add_handler(CommandHandler("start", start_command))  # Added /start command
    app.add_handler(CommandHandler("prefixes", prefixes_command))

    # Add handler for prefix selection
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^({'|'.join(PREFIXES)})$"), handle_prefix_selection))

    # Add handler for regular messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Add error handler
    app.add_error_handler(error)

    # Start polling
    print("Bot is running...")
    app.run_polling(poll_interval=3)
