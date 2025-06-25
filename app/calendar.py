import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Add this to your calendar.py
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # For Streamlit deployment:
            if 'STREAMLIT' in os.environ:
                creds = flow.run_local_server(port=8501)  # Streamlit's port
            else:
                creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def check_availability(service, start_time, end_time):
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()
    
    events_result = service.freebusy().query(
        body={
            "timeMin": start_time,
            "timeMax": end_time,
            "timeZone": 'UTC',
            "items": [{"id": 'primary'}]
        }
    ).execute()
    
    return not events_result['calendars']['primary']['busy']

def create_event(service, summary, start_time, end_time, timezone='UTC'):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')