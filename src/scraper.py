import time
import random
import re
import requests
import statistics
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_category_floor(model, year):
    """
    Returns an absolute minimum baseline floor based on vehicle tier and model year.
    No listing below this baseline can ever be classified as 'Full Price'.
    """
    model_lower = model.lower()
    
    # Tier 1: Luxury / Full-Size Premium SUVs / High-End Vans
    tier1 = [
        "patrol", "land cruiser", "prado", "alphard", "mustang", "explorer", 
        "expedition", "navigator", "tahoe", "suburban", "v-class", "carnival"
    ]
    
    # Tier 2: Mid/Full SUVs, Pickups, & Full-Size Vans
    tier2 = [
        "hiace", "fortuner", "terra", "montero", "everest", "navara", "hilux", 
        "triton", "strada", "cr-v", "hr-v", "mux", "mu-x", "ioniq", "santa fe", 
        "palisade", "odyssey", "sorento", "staria", "d-max", "ranger", "glc"
    ]

    # Tier 3: Compact MPVs, Crossovers, & Mid-Sedans
    tier3 = [
        "innova", "xpander", "avanza", "br-v", "rush", "veloz", "livina", 
        "kicks", "corolla cross", "yaris cross", "stargazer", "custin", 
        "civic", "altis", "elantra", "sylphy", "mazda3"
    ]

    # Determine Model Tier
    if any(m in model_lower for m in tier1):
        tier = 1
    elif any(m in model_lower for m in tier2):
        tier = 2
    elif any(m in model_lower for m in tier3):
        tier = 3
    else:
        tier = 4  # Economy Sedans / Small Hatchbacks (Vios, City, Brio, Wigo, Mirage, Almera, Yaris)

    # Apply Year Matrix Floor Rules
    if tier == 1:
        return 1200000 if year >= 2020 else 800000
    elif tier == 2:
        if year >= 2022:
            return 850000  # Strictly blocks ₱468k DP listings for 2022+ Staria, Hiace, Santa Fe
        elif year >= 2018:
            return 650000
        else:
            return 450000
    elif tier == 3:
        if year >= 2022:
            return 600000  # Floor for 2022+ Innova, Stargazer, Civic, Elantra
        elif year >= 2018:
            return 450000
        else:
            return 300000
    else:
        # Tier 4: Economy Sedans / Hatchbacks
        if year >= 2022:
            return 400000
        elif year >= 2017:
            return 280000
        else:
            return 180000

def calculate_automated_price_floor(raw_prices, model, year_hint=2023):
    """Combines statistical quantile analysis with the hard category baseline floor."""
    category_baseline = get_category_floor(model, year_hint)
    
    if not raw_prices or len(raw_prices) < 2:
        return category_baseline

    sorted_prices = sorted(raw_prices)
    max_price = sorted_prices[-1]

    p75 = statistics.quantiles(sorted_prices, n=4)[2] if len(sorted_prices) >= 4 else max_price
    dynamic_floor = int(p75 * 0.45)

    # The floor is ALWAYS at least the category baseline floor
    return max(dynamic_floor, category_baseline)

def build_model_url(make, model):
    slug = f"used-{make.lower()}-{model.lower().replace(' ', '-')}-for-sale"
    return f"https://philkotse.com/{slug}"

def fetch_page(url):
    time.sleep(random.uniform(2.5, 4.0))
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed fetching {url}: {e}")
    return None

def parse_model_listings(html_content, make, model):
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    listings = []
    heading_elements = soup.find_all("h3", class_="title")
    target_make_model = f"{make} {model}"

    for h3 in heading_elements:
        try:
            raw_title = h3.text.strip()
            if not any(char.isdigit() for char in raw_title[:6]) or "Philkotse" in raw_title:
                continue

            card = h3.find_parent(["div", "li", "article"])
            if not card:
                continue

            year_match = re.search(r'\b(19|20)\d{2}\b', raw_title)
            year = int(year_match.group(0)) if year_match else None

            price_elem = card.select_one(".price, .car-price, .item-price, .price-main, .pv-price")
            price_text = price_elem.text.strip() if price_elem else card.get_text()

            price_match = re.search(r'(?:₱|PHP|P)?\s*([1-9]\d{2,3},?\d{3})', price_text)
            if price_match:
                raw_price = int(price_match.group(1).replace(",", ""))
                if year:
                    listings.append({
                        "year": year,
                        "make_model": target_make_model,
                        "raw_price": raw_price
                    })
        except Exception:
            continue

    return listings

def scrape_all_ssot_models(ssot_data, pages_per_model=3):
    master_raw_listings = []

    for make, models in ssot_data.items():
        print(f"\n=================== SCRAPING MAKE: {make.upper()} ===================")
        for model in models:
            base_url = build_model_url(make, model)
            print(f"--> Auto-Researching & Labeling {make} {model}...")

            model_raw_candidates = []
            for page in range(1, pages_per_model + 1):
                url = f"{base_url}?page={page}" if page > 1 else base_url
                html = fetch_page(url)
                
                cars = parse_model_listings(html, make, model)
                if not cars:
                    break
                model_raw_candidates.extend(cars)

            if not model_raw_candidates:
                continue

            # Apply floor logic per listing year
            for car in model_raw_candidates:
                extracted_prices = [c["raw_price"] for c in model_raw_candidates if c["year"] == car["year"]]
                calculated_floor = calculate_automated_price_floor(extracted_prices, model, car["year"])

                if car["raw_price"] >= calculated_floor:
                    car["price_type"] = "Full Price"
                else:
                    car["price_type"] = "Downpayment / Promo"

            dp_count = sum(1 for c in model_raw_candidates if c["price_type"] == "Downpayment / Promo")
            full_count = len(model_raw_candidates) - dp_count
            print(f"    Total: {len(model_raw_candidates)} | Full Price: {full_count} | Downpayments: {dp_count}")

            master_raw_listings.extend(model_raw_candidates)

    return master_raw_listings