import unittest
from unittest.mock import patch, AsyncMock
from server import calendar_analysis
from server import duration
import asyncio

class TestDurationHelper(unittest.TestCase):
    def test_duration_basic(self):
        start = {"dateTime": "2025-05-16T21:45:00-04:00"}
        end = {"dateTime": "2025-05-16T22:45:00-04:00"}
        self.assertEqual(duration(start, end), 60)

    def test_duration_zero(self):
        start = {"dateTime": "2025-05-16T21:45:00-04:00"}
        end = {"dateTime": "2025-05-16T21:45:00-04:00"}
        self.assertEqual(duration(start, end), 0)

    def test_duration_missing_fields(self):
        start = {"dateTime": None}
        end = {"dateTime": "2025-05-16T22:45:00-04:00"}
        self.assertEqual(duration(start, end), 0)
        start = {"dateTime": "2025-05-16T21:45:00-04:00"}
        end = {"dateTime": None}
        self.assertEqual(duration(start, end), 0)
        self.assertEqual(duration({}, {}), 0)

    def test_duration_with_z_timezone(self):
        start = {"dateTime": "2025-05-16T21:45:00Z"}
        end = {"dateTime": "2025-05-16T22:45:00Z"}
        self.assertEqual(duration(start, end), 60)

    def test_duration_cross_day(self):
        start = {"dateTime": "2025-05-16T23:30:00-04:00"}
        end = {"dateTime": "2025-05-17T00:30:00-04:00"}
        self.assertEqual(duration(start, end), 60)

    def test_duration_negative(self):
        start = {"dateTime": "2025-05-16T22:45:00-04:00"}
        end = {"dateTime": "2025-05-16T21:45:00-04:00"}
        self.assertEqual(duration(start, end), -60)

class TestCalendarAnalysis(unittest.TestCase):
    @patch("server.service.events")
    def test_calendar_analysis_sums_by_color(self, mock_events):
        # Mock the API response
        mock_events.return_value.list.return_value.execute.return_value = {
            "items": [
                {"colorId": "1", "start": {"dateTime": "2025-05-16T10:00:00-04:00"}, "end": {"dateTime": "2025-05-16T11:00:00-04:00"}},
                {"colorId": "1", "start": {"dateTime": "2025-05-16T12:00:00-04:00"}, "end": {"dateTime": "2025-05-16T13:30:00-04:00"}},
                {"colorId": "2", "start": {"dateTime": "2025-05-16T14:00:00-04:00"}, "end": {"dateTime": "2025-05-16T15:00:00-04:00"}},
                {"start": {"dateTime": "2025-05-16T16:00:00-04:00"}, "end": {"dateTime": "2025-05-16T17:00:00-04:00"}},  # No colorId
            ]
        }
        result = asyncio.run(calendar_analysis("2025-05-16", "2025-05-17"))
        self.assertEqual(result, '{"1": 150, "2": 60}')

    @patch("server.service.events")
    def test_calendar_analysis_empty(self, mock_events):
        mock_events.return_value.list.return_value.execute.return_value = {"items": []}
        result = asyncio.run(calendar_analysis("2025-05-16", "2025-05-17"))
        self.assertEqual(result, '{}')

class TestMapColor(unittest.TestCase):
    @patch("server.service.colors")
    def test_map_color_found(self, mock_colors):
        # Mock the API response for colors().get().execute()
        mock_colors.return_value.get.return_value.execute.return_value = {
            "event": {
                "1": {"background": "#a4bdfc"},
                "2": {"background": "#7ae7bf"}
            }
        }
        from server import map_color
        result = asyncio.run(map_color("1"))
        self.assertEqual(result, "#a4bdfc")
        result = asyncio.run(map_color("2"))
        self.assertEqual(result, "#7ae7bf")

    @patch("server.service.colors")
    def test_map_color_not_found(self, mock_colors):
        mock_colors.return_value.get.return_value.execute.return_value = {
            "event": {
                "1": {"background": "#a4bdfc"}
            }
        }
        from server import map_color
        result = asyncio.run(map_color("999"))
        self.assertEqual(result, None)

if __name__ == "__main__":
    unittest.main()
