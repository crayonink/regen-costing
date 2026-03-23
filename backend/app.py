"""
REGEN Burner - Flask Backend API
Supports all KW ratings: 500, 1000, 1500, 2000, 2500, 3000, 4500, 6000
Run: python app.py
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from regen_costing import generate_costing, SUPPORTED_KW, DEFAULT_BLOWER_HP, DEFAULT_SPM
from google_sheets import create_costing_sheet

app = Flask(__name__)
CORS(app)

VALID_BLOWER_HP = [5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60]
SECTIONS = [
    "Burner & Pilot", "Gas Line - Pilot", "Gas Line - Burner",
    "Air Line - UV/Pilot", "Air Line - Burner", "Temperature Control",
    "Blower", "Controls & Gas Train"
]


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "REGEN Costing API is running"})


@app.route("/api/options", methods=["GET"])
def options():
    return jsonify({
        "supported_kw":     SUPPORTED_KW,
        "blower_hp_options": VALID_BLOWER_HP,
        "thermocouple_types": ["K", "R"],
        "default_blower_hp": DEFAULT_BLOWER_HP,
        "default_spm":       DEFAULT_SPM,
        "sections":          SECTIONS,
    })


@app.route("/api/costing", methods=["POST"])
def costing():
    """
    Generate costing and optionally create a Google Sheet.

    Expected JSON body:
    {
        "kw": 1000,
        "selling_price_multiplier": 1.8,
        "num_pairs": 2,
        "blower_hp": 10,
        "thermocouple_type": "K",
        "pipeline_cost_extra": 0,
        "company_name": "Tata Steel",
        "company_address": "Mumbai",
        "project": "Ladle Preheater",
        "export_to_sheets": true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # Costing inputs
        kw            = int(data.get("kw", 1000))
        spm           = float(data.get("selling_price_multiplier") or DEFAULT_SPM.get(kw, 1.8))
        num_pairs     = int(data.get("num_pairs", 2))
        blower_hp     = float(data.get("blower_hp") or DEFAULT_BLOWER_HP.get(kw, 10))
        thermo_type   = str(data.get("thermocouple_type", "K")).upper()
        pipeline_cost = float(data.get("pipeline_cost_extra", 0))

        # Customer details
        company_name    = str(data.get("company_name", "")).strip()
        company_address = str(data.get("company_address", "")).strip()
        project         = str(data.get("project", "")).strip()
        export_sheets   = bool(data.get("export_to_sheets", False))

        # Validate
        if kw not in SUPPORTED_KW:
            return jsonify({"error": f"kw must be one of {SUPPORTED_KW}"}), 400
        if not (1.0 <= spm <= 5.0):
            return jsonify({"error": "selling_price_multiplier must be between 1.0 and 5.0"}), 400
        if not (1 <= num_pairs <= 50):
            return jsonify({"error": "num_pairs must be between 1 and 50"}), 400
        if blower_hp not in VALID_BLOWER_HP:
            return jsonify({"error": f"blower_hp must be one of {VALID_BLOWER_HP}"}), 400
        if thermo_type not in ["K", "R"]:
            return jsonify({"error": "thermocouple_type must be K or R"}), 400
        if pipeline_cost < 0:
            return jsonify({"error": "pipeline_cost_extra cannot be negative"}), 400

        # Generate costing
        items, total_cost, total_sell, grand_total = generate_costing(
            kw=kw,
            selling_price_multiplier=spm,
            pipeline_cost_extra=pipeline_cost,
            blower_hp=blower_hp,
            thermocouple_type=thermo_type,
            num_pairs=num_pairs,
        )

        inputs_out = {
            "kw":                      kw,
            "selling_price_multiplier": spm,
            "num_pairs":               num_pairs,
            "blower_hp":               blower_hp,
            "thermocouple_type":       thermo_type,
            "pipeline_cost_extra":     pipeline_cost,
        }

        summary = {
            "total_cost":        round(total_cost, 2),
            "total_sell":        round(total_sell, 2),
            "grand_total":       round(grand_total, 2),
            "grand_total_lakhs": round(grand_total / 100000, 2),
        }

        response = {
            "inputs":   inputs_out,
            "summary":  summary,
            "sections": SECTIONS,
            "items":    items,
            "sheet":    None,
        }

        # Export to Google Sheets if requested
        if export_sheets:
            try:
                display_name = company_name or "Customer"
                sheet_info = create_costing_sheet(
                    company_name=display_name,
                    project=project or "Project",
                    inputs=inputs_out,
                    summary=summary,
                    items=items,
                )
                response["sheet"] = sheet_info
            except Exception as e:
                # Don't fail the whole request if sheets export fails
                response["sheet_error"] = str(e)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  REGEN Costing API starting...")
    print("  URL : http://localhost:5000")
    print("  Test: http://localhost:5000/api/health")
    print(f"  Supported KW: {SUPPORTED_KW}")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)