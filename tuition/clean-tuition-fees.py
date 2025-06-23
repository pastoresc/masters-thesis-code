import pandas as pd
import re

# Define exchange rates (June 2025)
conversion_rates = {
    "€": 1.0,
    "EUR": 1.0,
    "SGD": 0.69,
    "CAD": 0.68,
    "USD": 0.93,
    "$": 0.93
}

# Extract all numeric amounts
def extract_amounts(text):
    if pd.isna(text):
        return []
    text_clean = text.replace(" ", "")
    matches = re.findall(r"\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?", text_clean)
    nums = []
    for m in matches:
        if "," in m and "." in m:
            val = float(m.replace(",", ""))
        elif "," in m and "." not in m:
            val = float(m.replace(",", ""))
        else:
            val = float(m)
        nums.append(val)
    return nums

# Main row-processing function
def process_row(row):
    fee = row["Tuition Fees"]
    inst = row["Institution"].lower() if isinstance(row["Institution"], str) else ""
    result = {
        "EU": None,
        "International": None,
        "tuitionAmounts": ""
    }

    if pd.isna(fee) or fee.strip().lower() in ["", "not specified", "varies"]:
        return result

    fee_str_original = fee.strip()
    lowered_full = fee_str_original.lower()

    # UPCFIB (Universitat Politècnica de Catalunya)
    if "universitat politècnica de catalunya" in inst:
        result["EU"] = round(1661 / 3, 2)
        result["International"] = round(9496 / 3, 2)
        result["tuitionAmounts"] = "1661, 9496"
        return result

    # NUS (National University of Singapore)
    if "national university of singapore" in inst and "70,632" in lowered_full:
        result["International"] = round(70632 * conversion_rates["SGD"] / 4, 2)
        result["tuitionAmounts"] = "70632"
        return result

    # UOH (University of Helsinki)
    if "university of helsinki" in inst:
        result["International"] = round(15000 / 2, 2)
        result["tuitionAmounts"] = "15000"
        return result

    # UCPH (University of Copenhagen)
    if "university of copenhagen" in inst:
        nums = extract_amounts(fee_str_original)
        result["EU"] = 0.0
        if nums:
            nums_sorted = sorted(nums)
            high = nums_sorted[-1]
            result["International"] = round(high * conversion_rates["EUR"] * 0.5, 2)
            result["tuitionAmounts"] = ", ".join(str(int(v)) for v in nums_sorted)
        return result

    # Determine frequency factor (per semester conversion)
    if "per academic year" in lowered_full or "per year" in lowered_full or "non-eu" in lowered_full:
        factor = 0.5
    elif "total" in lowered_full:
        factor = 0.25
    else:
        factor = 1.0

    # Split into parts by "/" or " or "
    parts = re.split(r"/| or ", fee_str_original)
    values_extracted = []

    for part in parts:
        part_low = part.lower()

        # Detect currency
        if "cad" in part_low:
            symbol = "CAD"
        elif "usd" in part_low or "$" in part:
            symbol = "USD"
        elif "sgd" in part_low:
            symbol = "SGD"
        elif "eur" in part_low or "€" in part:
            symbol = "EUR"
        else:
            symbol = None

        if not symbol:
            continue

        match = re.search(r"\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?", part)
        if not match:
            continue

        raw = match.group()
        if "," in raw and "." in raw:
            val = float(raw.replace(",", ""))
        elif "," in raw and "." not in raw:
            val = float(raw.replace(",", ""))
        else:
            val = float(raw)
        values_extracted.append(str(int(val)))

        eur_val = val * conversion_rates[symbol] * factor

        if "eu" in part_low and "non" not in part_low:
            result["EU"] = round(eur_val, 2)
        elif any(kw in part_low for kw in ["non-eu", "outside", "international", "non european", "non-european", "domestic"]):
            result["International"] = round(eur_val, 2)

    result["tuitionAmounts"] = ", ".join(values_extracted)

    # Fallback: If no International found, take highest numeric as International
    if result["International"] is None and values_extracted:
        nums = [float(v) for v in values_extracted]
        sym = next((s for s in conversion_rates if s in fee_str_original), "EUR")
        result["International"] = round(max(nums) * conversion_rates.get(sym, 1.0) * factor, 2)

    return result

# Load input data
df = pd.read_csv("master_programs_data_cleaned.csv")

# Apply extraction to each row
results = df.apply(process_row, axis=1)

# Build output columns
df["tuitionAmounts"] = [r["tuitionAmounts"] for r in results]
df["tuitionAmountEUR_EU (in semester)"] = [r["EU"] for r in results]
df["tuitionAmountEUR_International (in semester)"] = [r["International"] for r in results]

# Export and save to CSV
df_out = df[[
    "Program ID",
    "Program Title",
    "Institution",
    "Tuition Fees",
    "tuitionAmounts",
    "tuitionAmountEUR_EU (in semester)",
    "tuitionAmountEUR_International (in semester)"
]]
df_out.to_csv("tuitionFees_cleaned.csv", index=False)
print("[OK] File saved as tuitionFees_cleaned.csv")