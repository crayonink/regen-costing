"""
REGEN Burner - Google Sheets Integration (OAuth Version)
Creates a new Google Sheet in the logged-in user's Google Drive.
"""

import os
import pickle
from datetime import datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TOKEN_FILE = "token.pickle"
CREDS_FILE = os.path.join(os.path.dirname(__file__), "oauth_credentials.json")

SECTIONS = [
    "Burner & Pilot", "Gas Line - Pilot", "Gas Line - Burner",
    "Air Line - UV/Pilot", "Air Line - Burner", "Temperature Control",
    "Blower", "Controls & Gas Train"
]


# ─────────────────────────────────────────────────────────────
# AUTH (OAuth)
# ─────────────────────────────────────────────────────────────
def get_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDS_FILE,
            SCOPES
        )
        creds = flow.run_console()

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("sheets", "v4", credentials=creds)


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────
def create_costing_sheet(company_name, project, inputs, summary, items):
    service = get_service()

    # Title
    date_str = datetime.now().strftime("%d %b %Y")
    kw = inputs["kw"]
    title = f"REGEN {kw}KW - {company_name} - {date_str}"

    # Create sheet
    spreadsheet = service.spreadsheets().create(
        body={"properties": {"title": title}},
        fields="spreadsheetId"
    ).execute()

    spreadsheet_id = spreadsheet.get("spreadsheetId")

    # ── Build rows ───────────────────────────────────────────
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

    grand_row = len(rows) + 1

    rows.append(["", "GRAND TOTAL (Rounded)", "", "", "", "", "", summary["grand_total"]])
    rows.append(["", f"≈ Rs. {summary['grand_total_lakhs']} Lakhs", "", "", "", "", "", ""])

    # ── Write data ───────────────────────────────────────────
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    # ── Formatting ───────────────────────────────────────────
    requests = []

    # Title formatting
    requests.append({
        "repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"bold": True, "fontSize": 16}
                }
            },
            "fields": "userEnteredFormat.textFormat"
        }
    })

    # Header formatting
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startRowIndex": header_row - 1,
                "endRowIndex": header_row
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"bold": True},
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
        }
    })

    # Column widths
    col_widths = [40, 280, 80, 60, 130, 140, 130, 140, 160]

    for i, width in enumerate(col_widths):
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": i,
                    "endIndex": i + 1
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize"
            }
        })

    # Freeze header
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": 0,
                "gridProperties": {"frozenRowCount": header_row}
            },
            "fields": "gridProperties.frozenRowCount"
        }
    })

    # Number formatting
    for col_idx in [4, 5, 6, 7]:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": item_start_row - 1,
                    "endRowIndex": item_end_row + 4,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "#,##0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })

    # Apply formatting
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

    return {
        "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
        "title": title,
        "spreadsheet_id": spreadsheet_id,
    }