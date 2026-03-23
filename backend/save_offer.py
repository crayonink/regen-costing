import json
from database import get_connection


def save_offer(company_name, project, inputs, summary, items):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert into offers table
    cursor.execute("""
    INSERT INTO offers (
        company_name,
        project,
        inputs_json,
        summary_json,
        total_cost,
        total_sell,
        grand_total
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company_name,
        project,
        json.dumps(inputs),
        json.dumps(summary),
        summary["total_cost"],
        summary["total_sell"],
        summary["grand_total"]
    ))

    offer_id = cursor.lastrowid

    # Insert items
    item_rows = [
        (
            offer_id,
            item["description"],
            item["size"],
            item["qty"],
            item["cost_unit"],
            item["total_cost"],
            item["sell_unit"],
            item["total_sell"],
            item["section"]
        )
        for item in items
    ]

    cursor.executemany("""
    INSERT INTO items (
        offer_id, description, size, qty,
        cost_unit, total_cost, sell_unit, total_sell, section
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, item_rows)

    conn.commit()
    conn.close()

    return offer_id