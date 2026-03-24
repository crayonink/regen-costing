"""
REGEN Burner - Google Sheets Integration (OAuth Version - Railway Safe)
"""

import os
import json
import pickle
import base64
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
# AUTH (OAuth) — RAILWAY SAFE
# ─────────────────────────────────────────────────────────────
def get_service():
    creds = None

    # 1. Try loading token from env variable (Railway production)
    token_b64 = os.environ.get("TOKEN_PICKLE_B64")

    print("DEBUG: TOKEN_PICKLE_B64 exists:", bool(token_b64))

    if token_b64:
        try:
            decoded = base64.b64decode(token_b64)
            creds = pickle.loads(decoded)
            print("✓ Loaded credentials from TOKEN_PICKLE_B64 env var")
        except Exception as e:
            print(f"✗ Failed to decode TOKEN_PICKLE_B64: {e}")
            raise Exception(f"TOKEN_PICKLE_B64 decode failed: {e}")

    # 2. Fallback to local token.pickle file (local development)
    if not creds and os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
            print("✓ Loaded credentials from token.pickle file")
        except Exception as e:
            print(f"✗ Failed to load token.pickle: {e}")
            raise Exception(f"token.pickle load failed: {e}")

    # 3. No credentials found — fail clearly
    if not creds:
        raise Exception(
            "No valid credentials found. "
            "Set TOKEN_PICKLE_B64 environment variable in Railway."
        )

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

    rows.append([
        "#", "Description", "Size", "Qty",
        "Cost/Unit (Rs.)", "Total Cost (Rs.)",
        "Sell/Unit (Rs.)", "Total Sell (Rs.)", "Section"
    ])

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