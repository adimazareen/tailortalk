import os
from datetime import datetime, timedelta
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import streamlit as st

# Use mock mode if no Google credentials are available
USE_MOCK = not os.path.exists('credentials.json') and 'google_auth' not in st.secrets

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    if USE_MOCK:
        return None
    
    creds = None
    
    # Try to load from Streamlit secrets first
    if 'google_auth' in st.secrets:
        creds = Credentials.from_authorized_user_info(
            st.secrets["google_auth"],
            SCOPES
        )
    
    # Fall back to local files
    if not creds and os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if 'google_auth' in st.secrets:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": st.secrets["google_auth"]["client_id"],
                            "client_secret": st.secrets["google_auth"]["client_secret"],
                            "redirect_uris": ["http://localhost"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    SCOPES
                )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            
            creds = flow.run_local_server(port=0)
        
        # Save credentials if using local files
        if not 'google_auth' in st.secrets and not USE_MOCK:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds) if not USE_MOCK else None

def check_availability(service, start_time: datetime, end_time: datetime) -> bool:
    if USE_MOCK:
        # Mock availability - always returns True for odd hours
        return start_time.hour % 2 == 1
    
    start_iso = start_time.isoformat()
    end_iso = end_time.isoformat()
    
    events_result = service.freebusy().query(
        body={
            "timeMin": start_iso,
            "timeMax": end_iso,
            "timeZone": 'UTC',
            "items": [{"id": 'primary'}]
        }
    ).execute()
    
    return not events_result['calendars']['primary']['busy']

def create_event(service, summary: str, start_time: datetime, end_time: datetime, timezone: str = 'UTC') -> str:
    if USE_MOCK:
        return f"https://calendar.example.com/mock-event-{start_time.timestamp()}"
    
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
    return event.get('htmlLink', "https://calendar.google.com")