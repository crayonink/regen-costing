"""
REGEN Burner - Google Sheets Integration (OAuth Version - Render Safe)
"""

import os
import json
import pickle
from datetime import datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TOKEN_FILE = "token.pickle"

SECTIONS = [
    "Burner & Pilot", "Gas Line - Pilot", "Gas Line - Burner",
    "Air Line - UV/Pilot", "Air Line - Burner", "Temperature Control",
    "Blower", "Controls & Gas Train"
]


# ─────────────────────────────────────────────────────────────
# AUTH (OAuth) — UPDATED
# ─────────────────────────────────────────────────────────────
def get_service():
    creds = None

    # Load token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no creds → load from ENV instead of file
    if not creds:
        creds_json = os.environ.get("OAUTH_CREDENTIALS")

        if not creds_json:
            raise Exception("OAUTH_CREDENTIALS not set in environment")

        creds_dict = json.loads(creds_json)

        # Write temp credentials file (required by Google library)
        temp_creds_path = "temp_oauth.json"
        with open(temp_creds_path, "w") as f:
            json.dump(creds_dict, f)

        flow = InstalledAppFlow.from_client_secrets_file(
            temp_creds_path,
            SCOPES
        )

        creds = flow.run_console()

        # Save token for reuse
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("sheets", "v4", credentials=creds)


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────
def create_costing_sheet(company_name, project, inputs, summary, items):
    service = get_service()

    date_str = datetime.now().strftime("%d %b %Y")
    kw = inputs["kw"]
    title = f"REGEN {kw}KW - {company_name} - {date_str}"

    spreadsheet = service.spreadsheets().create(
        body={"properties": {"title": title}},
        fields="spreadsheetId"
    ).execute()

    spreadsheet_id = spreadsheet.get("spreadsheetId")

    rows = []

    rows.append([f"REGEN BURNER {kw} KW — COST SHEET"])
    rows.append([])

    rows.append(["Company", company_name, "", "Date", date_str])
    rows.append(["Project", project, "", "KW Rating", f"{kw} KW"])
    rows.append(["Pairs", inputs["num_pairs"], "", "Blower HP", f"{inputs['blower_hp']} HP"])
    rows.append(["Multiplier", f"{inputs['selling_price_multiplier']}x", "", "Thermocouple", f"Type {inputs['thermocouple_type']}"])
    rows.append([])

    header_row = len(rows) + 1

    rows.append([
        "#", "Description", "Size", "Qty",
        "Cost/Unit (Rs.)", "Total Cost (Rs.)",
        "Sell/Unit (Rs.)", "Total Sell (Rs.)", "Section"
    ])

    item_start_row = len(rows) + 1

    for i, item in enumerate(items, 1):
        rows.append([
            i,
            item["description"],
            item["size"],
            item["qty"],
            item["cost_unit"],
            item["total_cost"],
            item["sell_unit"],
            item["total_sell"],
            SECTIONS[item["section"]] if item["section"] < len(SECTIONS) else "",
        ])

    item_end_row = len(rows)

    rows.append([])

    rows.append(["", "SUBTOTAL", "", "", "", summary["total_cost"], "", summary["total_sell"]])

    pipeline = inputs.get("pipeline_cost_extra", 0)
    if pipeline > 0:
        rows.append(["", "Pipeline Cost Extra", "", "", "", "", "", pipeline])

    rows.append(["", "GRAND TOTAL (Rounded)", "", "", "", "", "", summary["grand_total"]])
    rows.append(["", f"≈ Rs. {summary['grand_total_lakhs']} Lakhs", "", "", "", "", "", ""])

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    return {
        "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
        "title": title,
        "spreadsheet_id": spreadsheet_id,
    }