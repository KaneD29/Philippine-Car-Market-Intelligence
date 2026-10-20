import os
import csv

def find_market_deals(threshold_percent=-15.0, input_filename="master_philippine_cars.csv", output_filename="top_deals.csv"):
    """Scans master CSV for genuine Full Price listings priced below market average."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "data")
    
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)

    if not os.path.exists(input_path):
        print(f"[ERROR] Could not find '{input_path}'. Run main.py first to generate the dataset!")
        return

    deals = []

    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Skip any downpayments
                if row.get("price_type") != "Full Price":
                    continue

                raw_comp = row["market_avg_comparison"].replace("%", "").strip()
                comp_value = float(raw_comp)

                if comp_value <= threshold_percent:
                    deals.append(row)
            except ValueError:
                continue

    deals.sort(key=lambda x: float(x["market_avg_comparison"].replace("%", "")))

    if not deals:
        print(f"No genuine deals found meeting the {threshold_percent}% discount threshold.")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["year", "make_model", "price", "price_type", "market_avg_comparison"])
            writer.writeheader()
            writer.writerows(deals)

        print(f"\n==================================================")
        print(f"         DEAL FINDER SUMMARY ({threshold_percent}% or better)")
        print(f"==================================================")
        print(f"Found {len(deals)} genuine high-value deals!")
        print(f"Saved deals output to: '{output_path}'\n")

        print(f"{'Year':<6} | {'Make & Model':<25} | {'Price':<12} | {'Type':<12} | {'Market Dev':<10}")
        print("-" * 75)
        for deal in deals[:10]:
            print(f"{deal['year']:<6} | {deal['make_model']:<25} | {deal['price']:<12} | {deal['price_type']:<12} | {deal['market_avg_comparison']:<10}")

    except PermissionError:
        print(f"\n[ERROR] Permission Denied: Could not write to '{output_path}'. Close Excel and re-run.")

if __name__ == "__main__":
    find_market_deals(threshold_percent=-15.0)