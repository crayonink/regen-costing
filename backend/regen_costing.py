"""
REGEN Burner - Unified Costing Generator
Supports: 500, 1000, 1500, 2000, 2500, 3000, 4500, 6000 KW
"""

import math

# ─── BOM Price Lists ──────────────────────────────────────────────────────────

PILOT_BURNER_PRICE         = 10000
BURNER_CONTROLLER_PRICE    = 3600
IGNITION_TRANSFORMER_PRICE = 3300
UV_SENSOR_PRICE            = 5500
PILOT_REGULATOR_PRICE      = 4400
PILOT_SOLENOID_PRICE       = 4300
FLEXIBLE_HOSE_15_PRICE     = 1500
BALL_VALVE_15_PRICE        = 1400
PRESSURE_GAUGE_500_PRICE   = 3000
PRESSURE_GAUGE_1000_PRICE  = 4000
BALL_VALVE_UV_PRICE        = 1400
FLEX_HOSE_UV_PRICE         = 1500
BALL_VALVE_PILOT_PRICE     = 1400
FLEX_HOSE_PILOT_PRICE      = 1500
MANUAL_DAMPER_PRICE        = 40000
DPT_PRICE                  = 45000
THERMOCOUPLE_K_PRICE       = 5000
THERMOCOUPLE_R_PRICE       = 25000
PLC_PRICE                  = 300000

SOLENOID_VALVE_PRICES = {32:13700, 40:14720, 50:17900, 65:43000, 80:44000, 100:76000}
BALL_VALVE_PRICES     = {32:4925,  40:5100,  50:7200,  65:13400, 80:17000, 100:26600}
FLEX_HOSE_PRICES      = {32:1750,  40:2000,  50:3000,  65:4200,  80:6900,  100:7650}

SHUT_OFF_AIR_PRICES  = {125:50050, 200:80000, 250:125000, 300:148000, 350:177000, 400:227500}
MANUAL_BF_AIR_PRICES = {125:12498, 200:31178, 250:38378,  300:48055,  350:61700,  400:83750}
SHUT_OFF_FLUE_PRICES = {200:80000, 250:125000, 300:148000, 350:177000, 400:227500,
                         450:361020, 500:453470, 600:838150, 700:1048800}

AIR_CONTROL_VALVE_PRICES = {
    100:110450, 150:125600, 200:144000, 250:189540, 300:213240,
    350:242250, 400:258503, 450:327583, 500:396680, 600:561425,
    650:625771, 700:804856
}
AIR_FLOW_METER_PRICES = {
    125:54000, 200:57000, 250:58000, 300:60000, 350:64000,
    400:70500, 450:80500, 500:90500, 600:100500, 650:110500, 700:120500
}
GAS_CONTROL_VALVE_PRICES = {
    25:83000, 32:83000, 40:83000, 50:96960, 65:97810, 80:101900,
    100:110450, 150:125600, 200:144000, 250:189540, 300:213240, 350:242250, 400:261000
}
GAS_FLOW_METER_PRICES = {
    32:48000, 40:49000, 50:49700, 65:50000, 80:51000, 100:52000,
    150:54000, 200:57000, 250:58000, 300:60000, 350:64000, 400:70500
}
PNEUMATIC_DAMPER_PRICES = {
    200:80000, 250:125000, 300:148000, 350:177000, 400:350000,
    450:350000, 500:350000, 600:350000, 650:625771
}

BLOWER_BASE_PRICES = {
    5:56500, 7.5:60500, 10:76000, 15:87000, 20:91000,
    25:111000, 30:131000, 40:151500, 50:175000, 60:198000
}

CONTROL_PANEL_PRICES = {
    500:300000, 1000:300000, 1500:450000, 2000:450000,
    2500:600000, 3000:600000, 4500:600000, 6000:700000
}

NG_GAS_TRAIN_PRICES = {
    500:88500, 1000:110000, 1500:139300, 2000:144100,
    2500:224000, 3000:224000, 4500:295200, 6000:383000
}

# Burner + Regenerator cost per KW (from Burner Sizing sheet)
BURNER_REGEN_COSTS = {
    500:  124429.13,
    1000: 162998.63,
    1500: 196797.43,
    2000: 346253.53,
    2500: 356349.12,
    3000: 474790.79,
    4500: 663539.31,
    6000: 868568.06,
}

# Pipe sizes per KW (Air DN, Gas DN, Flue DN) — from Burner Pipe Size sheet
PIPE_SIZES = {
    500:  {"air_dn": 125, "gas_dn": 32, "flue_dn": 200},
    1000: {"air_dn": 200, "gas_dn": 40, "flue_dn": 250},
    1500: {"air_dn": 200, "gas_dn": 50, "flue_dn": 300},
    2000: {"air_dn": 250, "gas_dn": 65, "flue_dn": 350},
    2500: {"air_dn": 250, "gas_dn": 65, "flue_dn": 400},
    3000: {"air_dn": 300, "gas_dn": 80, "flue_dn": 450},
    4500: {"air_dn": 350, "gas_dn": 80, "flue_dn": 500},
    6000: {"air_dn": 400, "gas_dn": 350, "flue_dn": 700},
}

# Default blower HP per KW
DEFAULT_BLOWER_HP = {
    500: 10, 1000: 10, 1500: 15, 2000: 20,
    2500: 25, 3000: 25, 4500: 40, 6000: 60
}

# Default selling price multiplier per KW (6000KW uses 2.0, rest 1.8)
DEFAULT_SPM = {
    500:1.8, 1000:1.8, 1500:1.8, 2000:1.8,
    2500:1.8, 3000:1.8, 4500:1.8, 6000:2.0
}

SUPPORTED_KW = [500, 1000, 1500, 2000, 2500, 3000, 4500, 6000]


def closest_key(d, val):
    return min(d.keys(), key=lambda k: abs(k - val))

def roundup(x, decimals=0):
    factor = 10 ** decimals
    return math.ceil(x / factor) * factor

def lookup(d, val):
    return d.get(val, d[closest_key(d, val)])


def generate_costing(
    kw: int = 1000,
    selling_price_multiplier: float = None,
    pipeline_cost_extra: float = 0,
    blower_hp: float = None,
    thermocouple_type: str = "K",
    num_pairs: int = 2,
):
    """
    Generate REGEN Burner costing for any supported KW rating.

    Parameters
    ----------
    kw                       : burner power rating (500/1000/1500/2000/2500/3000/4500/6000)
    selling_price_multiplier : markup factor (defaults to 1.8, 2.0 for 6000KW)
    pipeline_cost_extra      : extra pipeline cost
    blower_hp                : combustion blower HP (defaults per KW if None)
    thermocouple_type        : 'K' or 'R'
    num_pairs                : number of burner pairs
    """

    if kw not in SUPPORTED_KW:
        raise ValueError(f"kw must be one of {SUPPORTED_KW}")

    SPM = selling_price_multiplier or DEFAULT_SPM[kw]
    n   = num_pairs
    nh  = max(1, n // 2)

    thermo_price = THERMOCOUPLE_K_PRICE if thermocouple_type.upper() == "K" else THERMOCOUPLE_R_PRICE

    pipes   = PIPE_SIZES[kw]
    air_dn  = pipes["air_dn"]
    gas_dn  = pipes["gas_dn"]
    flue_dn = pipes["flue_dn"]

    hp = blower_hp or DEFAULT_BLOWER_HP[kw]
    blower_price = roundup(lookup(BLOWER_BASE_PRICES, hp) * 1.08, -4)

    burner_regen_cost = BURNER_REGEN_COSTS[kw]
    cp_price  = lookup(CONTROL_PANEL_PRICES, kw)
    gt_price  = lookup(NG_GAS_TRAIN_PRICES, kw)

    items = []

    def add(section, description, size, qty, cost_unit):
        total_cost = qty * cost_unit
        sell_unit  = cost_unit * SPM
        total_sell = sell_unit * qty
        items.append({
            "section":     section,
            "description": description,
            "size":        size,
            "qty":         qty,
            "cost_unit":   round(cost_unit, 2),
            "total_cost":  round(total_cost, 2),
            "sell_unit":   round(sell_unit, 2),
            "total_sell":  round(total_sell, 2),
        })

    # Section 0: Burner & Pilot
    add(0, f"Burner with Regenerator ({kw} KW)", f"{kw} KW", n, burner_regen_cost)
    add(0, "Pilot Burner", "7 KW", n, PILOT_BURNER_PRICE)
    add(0, "Burner Controller", "-", n, BURNER_CONTROLLER_PRICE)
    add(0, "Ignition Transformer", "-", n, IGNITION_TRANSFORMER_PRICE)
    add(0, "UV Sensor", "-", n, UV_SENSOR_PRICE)

    # Section 1: Gas Line - Pilot
    add(1, "Pilot Regulator", "NB15", n, PILOT_REGULATOR_PRICE)
    add(1, "Pilot Solenoid Valve", "NB15", n, PILOT_SOLENOID_PRICE)
    add(1, "Flexible Hose (Pilot)", "NB15", n, FLEXIBLE_HOSE_15_PRICE)
    add(1, "Ball Valve (Pilot)", "NB15", n, BALL_VALVE_15_PRICE)
    add(1, "Pressure Gauge 0-500mm", "-", n, PRESSURE_GAUGE_500_PRICE)

    # Section 2: Gas Line - Burner
    sv_price  = lookup(SOLENOID_VALVE_PRICES, gas_dn)
    bv_price  = lookup(BALL_VALVE_PRICES, gas_dn)
    fh_price  = lookup(FLEX_HOSE_PRICES, gas_dn)

    add(2, f"Solenoid Valve NB{gas_dn}", f"NB{gas_dn}", n, sv_price)
    add(2, f"Ball Valve NB{gas_dn}", f"NB{gas_dn}", n * 5, bv_price)
    add(2, f"Flex Hose NB{gas_dn}", f"NB{gas_dn}", n * 5, fh_price)
    add(2, f"3-Way Valve NB{gas_dn}", f"NB{gas_dn}", n, 0)
    add(2, "Pressure Gauge 0-500mm (Burner)", "-", n, PRESSURE_GAUGE_500_PRICE)

    # Section 3: Air Line - UV/Pilot
    add(3, "Ball Valve UV", "NB15", n * 4, BALL_VALVE_UV_PRICE)
    add(3, "Flex Hose UV", "NB15", n * 2, FLEX_HOSE_UV_PRICE)
    add(3, "Ball Valve Pilot", "NB15", n * 2, BALL_VALVE_PILOT_PRICE)
    add(3, "Flex Hose Pilot", "NB15", n * 2, FLEX_HOSE_PILOT_PRICE)

    # Section 4: Air Line - Burner
    soa_price  = lookup(SHUT_OFF_AIR_PRICES, air_dn)
    mbfa_price = lookup(MANUAL_BF_AIR_PRICES, air_dn)
    sof_price  = lookup(SHUT_OFF_FLUE_PRICES, flue_dn)

    add(4, f"Shut-Off Valve Air NB{air_dn}", f"NB{air_dn}", n, soa_price)
    add(4, f"Manual BF Valve Air NB{air_dn}", f"NB{air_dn}", n, mbfa_price)
    add(4, "Pressure Gauge 0-1000mm", "-", n, PRESSURE_GAUGE_1000_PRICE)
    add(4, f"Shut-Off Valve Flue NB{flue_dn}", f"NB{flue_dn}", n, sof_price)
    add(4, f"Thermocouple TT-{thermocouple_type}", "-", n * 2, thermo_price)

    # Section 5: Temperature Control System
    acv_price = lookup(AIR_CONTROL_VALVE_PRICES, air_dn)
    afm_price = lookup(AIR_FLOW_METER_PRICES, air_dn)
    gcv_price = lookup(GAS_CONTROL_VALVE_PRICES, gas_dn)
    gfm_price = lookup(GAS_FLOW_METER_PRICES, gas_dn)
    pd_price  = lookup(PNEUMATIC_DAMPER_PRICES, flue_dn)

    add(5, f"Air Control Valve NB{air_dn}", f"NB{air_dn}", nh, acv_price)
    add(5, f"Air Flow Meter DPT NB{air_dn}", f"NB{air_dn}", nh, afm_price)
    add(5, f"Gas Control Valve NB{gas_dn}", f"NB{gas_dn}", nh, gcv_price)
    add(5, f"Gas Flow Meter DPT NB{gas_dn}", f"NB{gas_dn}", nh, gfm_price)
    add(5, "Thermocouple TT-R (TCS)", "-", nh, THERMOCOUPLE_R_PRICE)
    add(5, "DPT (flow/pressure/temp)", "1 unit", 1, DPT_PRICE)
    add(5, f"Pneumatic Damper NB{flue_dn}", f"NB{flue_dn}", nh, pd_price)
    add(5, "Manual Damper", "1 unit", 1, MANUAL_DAMPER_PRICE)

    # Section 6: Blower
    add(6, f"Combustion Blower {hp}HP/40\"", f"{hp}HP", n, blower_price)

    # Section 7: Controls & Gas Train
    add(7, "PLC with HMI", "-", 1, PLC_PRICE)
    add(7, "Control Panel", "-", 1, cp_price)
    add(7, f"NG Gas Train", "-", 1, gt_price)

    total_cost  = sum(i["total_cost"] for i in items)
    total_sell  = sum(i["total_sell"] for i in items)
    grand_total = roundup(total_sell + pipeline_cost_extra, -4)

    return items, round(total_cost, 2), round(total_sell, 2), round(grand_total, 2)


if __name__ == "__main__":
    for kw in SUPPORTED_KW:
        items, tc, ts, gt = generate_costing(kw=kw)
        print(f"{kw:>5} KW  |  Cost: Rs.{tc:>14,.0f}  |  Sell: Rs.{ts:>14,.0f}  |  Grand Total: Rs.{gt:>14,.0f}")
