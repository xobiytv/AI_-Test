import os
from datetime import datetime, timedelta
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PATH, GOOGLE_SCOPES, TIMEZONE


def get_calendar_service():
    creds = None
    if os.path.exists(GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_PATH, GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(GOOGLE_CREDENTIALS_PATH):
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_PATH, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(GOOGLE_TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        else:
            return None

    return build("calendar", "v3", credentials=creds)


async def create_calendar_event(
    title: str,
    description: str,
    start_dt: datetime,
    duration_minutes: int = 60,
) -> Optional[str]:
    try:
        service = get_calendar_service()
        if not service:
            return None

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 15},
                    {"method": "email", "minutes": 30},
                ],
            },
        }

        created = service.events().insert(calendarId="primary", body=event).execute()
        return created.get("id")
    except HttpError as e:
        print(f"Google Calendar error: {e}")
        return None
    except Exception as e:
        print(f"Calendar service unavailable: {e}")
        return None
