import os
import json
import csv
import statistics

def load_car_ssot():
    """Loads the official car models SSOT JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    ssot_path = os.path.join(project_dir, "data", "car_models.json")
    
    if os.path.exists(ssot_path):
        with open(ssot_path, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"Warning: SSOT file not found at {ssot_path}")
    return {}

def filter_outliers_and_calculate_market(listings):
    """Calculates market averages using ONLY Full Price listings while retaining labeled downpayments."""
    if not listings:
        return []

    # Group listings by make_model and year
    grouped = {}
    for item in listings:
        key = (item["make_model"], item["year"])
        grouped.setdefault(key, []).append(item)

    cleaned_listings = []

    for (make_model, year), cars in grouped.items():
        # Separate full-price listings for statistical calculation
        full_price_cars = [c for c in cars if c["price_type"] == "Full Price"]
        dp_cars = [c for c in cars if c["price_type"] == "Downpayment / Promo"]

        # Label downpayments with N/A comparison so they don't corrupt deal detection
        for dp in dp_cars:
            dp["price"] = f"₱{dp['raw_price']:,}"
            dp["market_avg_comparison"] = "N/A (DP)"
            del dp["raw_price"]
            cleaned_listings.append(dp)

        if not full_price_cars:
            continue

        prices = [c["raw_price"] for c in full_price_cars]
        median_price = statistics.median(prices)
        
        # Keep prices within 60% to 150% of the median
        valid_cars = [c for c in full_price_cars if 0.6 * median_price <= c["raw_price"] <= 1.5 * median_price]
        valid_prices = [c["raw_price"] for c in valid_cars]

        if valid_prices:
            avg_price = int(statistics.mean(valid_prices))
            
            for c in valid_cars:
                c["price"] = f"₱{c['raw_price']:,}"
                c["market_avg_comparison"] = f"{round((c['raw_price'] / avg_price - 1) * 100, 1):+}%"
                del c["raw_price"]
                cleaned_listings.append(c)

    return cleaned_listings

def save_master_csv(data, filename="master_philippine_cars.csv"):
    """Saves the complete dataset with price_type labels into the master CSV."""
    if not data:
        print("No listings found to save.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, filename)

    try:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["year", "make_model", "price", "price_type", "market_avg_comparison"])
            writer.writeheader()
            writer.writerows(data)
        print(f"\n[SUCCESS] Saved {len(data)} total listings to '{file_path}'")
    except PermissionError:
        print(f"\n[ERROR] Permission Denied: Please close '{file_path}' in Excel and re-run!")