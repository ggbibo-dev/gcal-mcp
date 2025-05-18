import json
# server.py
import datetime
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("notion")
import asyncio
import aiohttp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Google API Credentials
SERVICE_ACCOUNT_FILE = ".service_key.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Authenticate and create service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

# Load environment variables from .env
load_dotenv()
CALENDAR_ID = os.getenv("CALENDAR_ID")

# Add an addition tool
@mcp.tool()
async def calendar_analysis(start_date: str, end_date: str) -> tuple:
    """return start and end date as interpreted by llm"""
    # Parse start_date and end_date strings in "YYYY-MM-DD" format
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    events_result = await asyncio.to_thread(
        service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat() + "Z",
            timeMax=end_dt.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        ).execute
    )

    events = events_result.get("items", [])
    result = []
    for event in events:
        # result.append({
        #     "summary": event.get("summary"),
        #     "description": event.get("description"),
        #     "start": event.get("start"),
        #     "end": event.get("end"),
        #     "colorId": event.get("colorId"),
        # })
        result.append(event)
    return json.dumps(result)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.tool()
async def analyze_event(event_id: str) -> str:
    """Fetch and analyze a single event by its event_id."""
    event = await asyncio.to_thread(
        service.events().get(
            calendarId=CALENDAR_ID,
            eventId=event_id
        ).execute
    )
    # Example analysis: return summary and description
    return json.dumps(event)

if __name__ == "__main__":
    # Initialize and run the server
    # mcp.run(transport='stdio')
    # Fix: test with correct date order and print result
    result = asyncio.run(calendar_analysis("2025-05-17", "2025-05-18"))
    print(result)