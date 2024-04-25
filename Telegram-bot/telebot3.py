import os
import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define your Telegram bot token
TOKEN = '7059344269:AAHEJOLA67JP0j-IdtOtrEwXLuHjUXLyyYw'

# Define your Google Calendar API credentials file path1
CLIENT_SECRET_FILE_CALENDAR = 'D:\Telegram-bot\client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

GET_TITLE, GET_DATE, GET_TIME, GET_EMAIL, GET_PLATFORM = range(5)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Please provide the meeting title.")
    return GET_TITLE

def get_title(update: Update, context: CallbackContext):
    title = update.message.text
    context.user_data['title'] = title
    update.message.reply_text("Great! Now please enter the date (YYYY-MM-DD).")
    return GET_DATE

def get_date(update: Update, context: CallbackContext):
    date_str = update.message.text
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        update.message.reply_text("Please enter a valid date in the format YYYY-MM-DD.")
        return GET_DATE
    context.user_data['date'] = date
    update.message.reply_text("Awesome! Now please enter the time (HH:MM).")
    return GET_TIME

def get_time(update: Update, context: CallbackContext):
    time_str = update.message.text
    try:
        time = datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        update.message.reply_text("Please enter a valid time in the format HH:MM.")
        return GET_TIME
    context.user_data['time'] = time
    update.message.reply_text("Please enter your email address.")
    return GET_EMAIL

def get_email(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    update.message.reply_text("Choose the meeting platform:\n1. Google Meet\n2. Zoom\n3. Google Teams")
    return GET_PLATFORM

def get_platform(update: Update, context: CallbackContext):
    platform = update.message.text
    if platform not in ['1', '2', '3']:
        update.message.reply_text("Please choose a valid platform (1, 2, or 3).")
        return GET_PLATFORM

    platform_dict = {'1': 'Google Meet', '2': 'Zoom', '3': 'Google Teams'}
    context.user_data['platform'] = platform_dict[platform]

    # Schedule the meeting and send invitations
    schedule_and_send_invitations(update, context)
    return ConversationHandler.END

def schedule_and_send_invitations(update: Update, context: CallbackContext):
    title = context.user_data['title']
    date = context.user_data['date']
    time = context.user_data['time']
    email = context.user_data['email']
    platform = context.user_data['platform']

    # Authenticate Google Calendar API
    creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE_CALENDAR, SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    # Create an event for Google Calendar
    event = {
        'summary': title,
        'description': f'Meeting on {title} via {platform}',
        'start': {
            'dateTime': f'{date}T{time}:00',
            'timeZone': 'YOUR_TIME_ZONE',  # Specify your time zone here
        },
        'end': {
            'dateTime': f'{date}T{time}:00',
            'timeZone': 'YOUR_TIME_ZONE',  # Specify your time zone here
        },
        'attendees': [
            {'email': email},
        ],
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        update.message.reply_text("Meeting scheduled successfully!")
    except Exception as e:
        update.message.reply_text(f"Error scheduling the meeting: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_TITLE: [MessageHandler(Filters.text & ~Filters.command, get_title)],
            GET_DATE: [MessageHandler(Filters.text & ~Filters.command, get_date)],
            GET_TIME: [MessageHandler(Filters.text & ~Filters.command, get_time)],
            GET_EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
            GET_PLATFORM: [MessageHandler(Filters.text & ~Filters.command, get_platform)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
