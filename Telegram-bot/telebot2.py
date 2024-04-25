import os
import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Define your Telegram bot token
TOKEN = '7059344269:AAHEJOLA67JP0j-IdtOtrEwXLuHjUXLyyYw'

# Define your Gmail credentials
EMAIL = ''
PASSWORD = ''

GET_TITLE, GET_DATE, GET_DURATION, GET_CHANNEL, GET_EMAIL = range(5)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Please provide the meeting title.")
    return GET_TITLE

def get_title(update: Update, context: CallbackContext):
    title = update.message.text
    context.user_data['title'] = title
    update.message.reply_text("Great! Now please enter the meeting date (YYYY-MM-DD).")
    return GET_DATE

def get_date(update: Update, context: CallbackContext):
    date_str = update.message.text
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        update.message.reply_text("Please enter a valid date in the format YYYY-MM-DD.")
        return GET_DATE
    context.user_data['date'] = date
    update.message.reply_text("Enter the meeting time duration (HH:MM).")
    return GET_DURATION

def get_duration(update: Update, context: CallbackContext):
    duration_str = update.message.text
    try:
        duration = datetime.datetime.strptime(duration_str, "%H:%M").time()
    except ValueError:
        update.message.reply_text("Please enter a valid duration in the format HH:MM.")
        return GET_DURATION
    context.user_data['duration'] = duration
    update.message.reply_text("Choose the meeting channel:\n1. Google Meet\n2. Zoom\n3. Teams")
    return GET_CHANNEL

def get_channel(update: Update, context: CallbackContext):
    channel = update.message.text
    context.user_data['channel'] = channel
    update.message.reply_text("Please enter the email address to send the invitation.")
    return GET_EMAIL

def get_email(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    send_invitation(update, context)
    return ConversationHandler.END

def send_invitation(update: Update, context: CallbackContext):
    title = context.user_data['title']
    date = context.user_data['date']
    duration = context.user_data['duration']
    channel = context.user_data['channel']
    email = context.user_data['email']

    # Send the invitation via email
    send_email(title, date, duration, channel, email)

    response = f"Meeting Scheduled:\nTitle: {title}\nDate: {date}\nDuration: {duration}\nChannel: {channel}\nInvitation sent to: {email}"

    update.message.reply_text(response)

def send_email(title, date, duration, channel, email):
    message = MIMEMultipart()
    message['From'] = EMAIL
    message['To'] = email
    message['Subject'] = f"Invitation for Meeting: {title}"

    body = f"Meeting Title: {title}\nDate: {date}\nDuration: {duration}\nChannel: {channel}"
    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, email, message.as_string())

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_TITLE: [MessageHandler(Filters.text & ~Filters.command, get_title)],
            GET_DATE: [MessageHandler(Filters.text & ~Filters.command, get_date)],
            GET_DURATION: [MessageHandler(Filters.text & ~Filters.command, get_duration)],
            GET_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, get_channel)],
            GET_EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
