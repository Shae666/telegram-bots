from google_auth_oauthlib.flow import InstalledAppFlow
import json

CLIENT_SECRET_FILE_CALENDAR = 'D:\\Telegram-bot\\client_secret_calender.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

authorized_user_info = {
    "client_id": "963972309002-lv6mvn8eoh84juan5g0gnvoh0d1o678b.apps.googleusercontent.com",
    "client_secret": "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",
    "refresh_token": None,
    "token": None,
    "token_uri": "https://oauth2.googleapis.com/token",
    "scopes": SCOPES
}

def authenticate_google():
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": "963972309002-lv6mvn8eoh84juan5g0gnvoh0d1o678b.apps.googleusercontent.com",
                "project_id": "i-gateway-421305",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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",
                "redirect_uris": ["http://localhost"]
            }
        },
        scopes=SCOPES
    )
    creds = flow.run_local_server(port=0)
    authorized_user_info['token'] = creds.token
    authorized_user_info['refresh_token'] = creds.refresh_token

    with open('authorized_user_info.json', 'w') as json_file:
        json.dump(authorized_user_info, json_file)

if __name__ == '__main__':
    authenticate_google()
