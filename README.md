# Calendar API Setup

Follow these steps to set up the Notion Calendar API integration:

## 1. Set Up a Service Account in Google Cloud Platform (GCP)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **IAM & Admin > Service Accounts**.
4. Click **Create Service Account**.
5. Enter a name and description, then click **Create and Continue**.
6. Assign the **Editor** role (or a more restrictive role if preferred).
7. Click **Done**.
8. In the service account list, click on your new account and go to the **Keys** tab.
9. Click **Add Key > Create new key**.
10. Select **JSON** and click **Create**. Download and securely store the JSON key file.

## 2. Share the Calendar with the Service Account

1. Open [Google Calendar](https://calendar.google.com/).
2. Find the calendar you want to use and click the three dots next to it.
3. Select **Settings and sharing**.
4. Under **Share with specific people**, click **Add people**.
5. Enter the service account email (found in your JSON key file).
6. Set the permission to **Make changes to events**.
7. Click **Send**.

Your service account now has access to the calendar and can manage events via the API.

## 3. Configure Color Mappings

The application uses color IDs to categorize calendar events. You need to create a local configuration file to map these color IDs to meaningful category names.

1. Copy the sample configuration file:

   ```bash
   cp sample_color_mappings.json color_mappings.json
   ```

2. Edit `color_mappings.json` to define your personal category mappings. Each color ID (1-11) should have:
   - `meaning`: A descriptive name for the category
   - `color`: A friendly color name (used for display purposes)

   Example:

   ```json
   {
     "1": {"meaning": "Work meetings", "color": "lavender"},
     "2": {"meaning": "Exercise", "color": "tomato"},
     "3": {"meaning": "Personal time", "color": "sage"}
   }
   ```

3. In Google Calendar, assign colors to your events using the color picker. The application will automatically map these to your defined categories.

   **Note**: `color_mappings.json` is ignored by git to keep your personal categorizations private.

## 4. Environment Setup

Create a `.env` file with your calendar ID:

```
CALENDAR_ID=your-email@gmail.com
```

## 5. Installation and Usage

1. Install dependencies:

   ```bash
   uv pip install -r requirements.txt
   ```

2. Run the server:

   ```bash
   python server.py
   ```
