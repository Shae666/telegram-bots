import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import json

# Create an authorized user info dictionary with required fields
authorized_user_info = {
    "client_id": "963972309002-lv6mvn8eoh84juan5g0gnvoh0d1o678b.apps.googleusercontent.com",
    "client_secret": "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",
    "refresh_token": "YOUR_REFRESH_TOKEN",
    "token": None,  # This field can be None or filled later during authentication
    "token_uri": "https://oauth2.googleapis.com/token",
    "scopes": [
        "https://www.googleapis.com/auth/calendar"
    ]
}

# Write the authorized user info to a JSON file
with open('authorized_user_info.json', 'w') as json_file:
    json.dump(authorized_user_info, json_file)

print("Authorized user info has been written to 'authorized_user_info.json'.")


# Define your Telegram bot token
TOKEN = '7059344269:AAHEJOLA67JP0j-IdtOtrEwXLuHjUXLyyYw'

# Define your Google Calendar API credentials file path
CLIENT_SECRET_FILE_CALENDAR = 'D:\Telegram-bot\client_secret_calender.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

GET_TITLE, GET_DATE, GET_TIME, GET_EMAIL, GET_CHANNEL = range(5)

# Email credentials
EMAIL_ADDRESS = '22mcaa19@kristujayanti.com'
EMAIL_PASSWORD = '@francisbenilrex'

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
    update.message.reply_text("Finally, please enter the email address where you want to send the invitation.")
    return GET_EMAIL

def get_email(update: Update, context: CallbackContext):
    email = update.message.text

    # Store the email in user_data
    context.user_data['email'] = email

    # Ask for the meeting channel (e.g., Google Meet, Zoom, Teams)
    update.message.reply_text("Choose the meeting channel:\n1. Google Meet\n2. Zoom\n3. Teams")
    return GET_CHANNEL

def get_channel(update: Update, context: CallbackContext):
    channel = update.message.text
    context.user_data['channel'] = channel

    # Schedule the meeting and send invitations
    schedule_and_send_invitations(update, context)
    return ConversationHandler.END

def schedule_and_send_invitations(update: Update, context: CallbackContext):
    title = context.user_data['title']
    date = context.user_data['date']
    time = context.user_data['time']
    email = context.user_data['email']
    channel = context.user_data['channel']

    # Build the event details
    event = {
        'summary': title,
        'description': f'Meeting on {title}',
        'start': {
            'dateTime': f'{date}T{time}:00',
        },
        'end': {
            'dateTime': f'{date}T{time}:00',
        },
        'attendees': [
            {'email': email},
        ],
    }

    creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE_CALENDAR, SCOPES)
    service = build('calendar', 'v3', credentials=creds)

    event = service.events().insert(calendarId='primary', body=event).execute()

    # Generate meeting link based on the chosen channel
    if channel == '1':
        meeting_link = 'Google Meet link'
    elif channel == '2':
        meeting_link = 'Zoom link'
    elif channel == '3':
        meeting_link = 'Teams link'
    else:
        meeting_link = 'Unknown channel'

    # Send the meeting link to the specified email
    send_email(email, meeting_link)


    response = f"Meeting Scheduled:\nTitle: {title}\nDate: {date}\nTime: {time}\nEmail sent to: {email}\nChannel: {channel}"

    update.message.reply_text(response)

def send_email(to_email, meeting_link):
    subject = "Meeting Invitation"
    body = f"Hello,\n\nYou have been invited to a meeting. Please join using the following link: {meeting_link}\n\nBest regards,\nYour Team"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

def send_meeting_link(email, meeting_link, context):
    # Here you can implement the logic to send the meeting link to the specified email
    # You can use APIs or libraries for sending emails

    # Example code to send the link via Telegram
    context.bot.send_message(chat_id=email, text=f"Here is your meeting link: {meeting_link}")

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
            GET_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, get_channel)],
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
