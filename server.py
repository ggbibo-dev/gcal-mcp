import json
# server.py
import datetime
from typing import Optional
from mcp.server.fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("notion")
import asyncio
import aiohttp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from collections import defaultdict

# Google API Credentials
SERVICE_ACCOUNT_FILE = ".service_key.json"
COLOR_MAPPING_CONFIG = ".color_mappings.json"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

# Authenticate and create service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

# Load environment variables from .env
load_dotenv()
CALENDAR_ID = os.getenv("CALENDAR_ID")

# Load color meanings from local JSON config
def load_color_mappings():
    try:
        with open(COLOR_MAPPING_CONFIG, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("color_mappings.json not found, you won't be able to see the breakdown :(")
        return defaultdict()

COLOR_ID_MEANINGS = load_color_mappings()

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
            timeMin=start_dt.isoformat() + "-04:00",
            timeMax=end_dt.isoformat() + "-04:00",
            singleEvents=True,
            orderBy="startTime",
        ).execute
    )

    events = events_result.get("items", [])
    color_durations = defaultdict(int)
    for event in events:
        color_id = event.get("colorId")
        start = event.get("start", {})
        end = event.get("end", {})
        dur = duration(start, end)
        logger.info(f"Event color_id={color_id}, duration={dur} minutes")
        if color_id is None:
            color_id = "1"  # Default color ID if not specified
        if color_id != "null":
            color_durations[color_id] += dur

    # Map color IDs to human-readable names and color values
    breakdown = {}
    for color_id, total_duration in color_durations.items():
        color_value = await map_color(color_id)
        logger.info(f"Mapping color_id {color_id} to color value {color_value}")
        human_label = COLOR_ID_MEANINGS.get(color_id, {"meaning": f"Unknown ({color_id})", "color": "unknown"})
        breakdown[human_label["meaning"]] = {
            "duration": total_duration,
            "color": color_value.get("background") if color_value else None,
            "color_name": human_label["color"]
        }

    total = sum(item["duration"] for item in breakdown.values())
    # Calculate available and wasted
    num_days = (end_dt - start_dt).days
    if num_days < 1:
        num_days = 1
    available = num_days * 24 * 60
    wasted = available - total
    return json.dumps({
        "breakdown": breakdown,
        "total": total,
        "available": available,
        "wasted": wasted
    })


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def duration(event_start: dict, event_end: dict) -> int:
    """Calculate the duration in minutes between event_start and event_end objects using datetime.fromisoformat."""
    start_str = event_start.get("dateTime")
    end_str = event_end.get("dateTime")
    if not start_str or not end_str:
        return 0
    
    start_dt = datetime.fromisoformat(start_str)
    end_dt = datetime.fromisoformat(end_str)
    delta = end_dt - start_dt
    return int(delta.total_seconds() // 60)

async def map_color(color_id: str) -> Optional[dict]:
    """Fetch the color value for a given colorId from Google Calendar Colors API."""
    colors_result = await asyncio.to_thread(service.colors().get().execute)
    # logger.info(f"colors_result: {json.dumps(colors_result, indent=2)}")
    event_colors = colors_result.get("event", {})
    color_info = event_colors.get(color_id, {})
    return color_info


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')