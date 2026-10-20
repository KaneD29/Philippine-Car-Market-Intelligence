import time
from utils import load_car_ssot, filter_outliers_and_calculate_market, save_master_csv
from scraper import scrape_all_ssot_models
from deal_finder import find_market_deals

def main():
    start_time = time.perf_counter()
    print("Initializing Philippine Car Market Scraper...")
    
    ssot_data = load_car_ssot()
    if not ssot_data:
        print("Scraper aborted. Please populate 'data/car_models.json'.")
        return

    # 1. Scrape listings
    raw_listings = scrape_all_ssot_models(ssot_data, pages_per_model=2)
    print(f"\nRaw candidates collected across all models: {len(raw_listings)}")

    # 2. Filter outliers and calculate market averages
    cleaned_listings = filter_outliers_and_calculate_market(raw_listings)
    print(f"Valid listings retained after outlier filtering: {len(cleaned_listings)}")

    # 3. Save master dataset
    save_master_csv(cleaned_listings, "master_philippine_cars.csv")

    # 4. Trigger deal finder analysis on the fresh dataset
    find_market_deals(threshold_percent=-15.0)

    end_time = time.perf_counter()
    elapsed_seconds = end_time - start_time
    minutes = int(elapsed_seconds // 60)
    seconds = elapsed_seconds % 60
    
    print(f"\n==================================================")
    print(f"Total Execution Time: {minutes}m {seconds:.2f}s ({elapsed_seconds:.2f} seconds)")
    print(f"==================================================")

if __name__ == "__main__":
    main()