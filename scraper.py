import json
import time
import random
import re
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGETS = [
    {
        "brand": "MyProtein",
        "url": "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
        "selectors": { "price": ".price-with-discounts" },
        "fixed_name": "Impact Whey Protein",
        "default_purity": 72,
        "fixed_weight": 1.0,
        "local_image": "img/myprotein.jpg",
        "affiliate_link": None
    },
    {
        "brand": "HSN",
        "url": "https://www.hsnstore.com/marcas/sport-series/evowhey-protein",
        "selectors": { "price": ".price-container .price" },
        "fixed_name": "Evowhey Protein 2.0",
        "default_purity": 78,
        "fixed_weight": 0.5,
        "local_image": "img/hsn.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Prozis",
        "url": "https://www.prozis.com/es/es/prozis/100-real-whey-protein-1000-g",
        "selectors": { "price": ".final-price" },
        "fixed_name": "100% Real Whey Protein",
        "default_purity": 80,
        "fixed_weight": 1.0,
        "local_image": "img/prozis.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Optimum Nutrition",
        "url": "https://www.optimumnutrition.com/products/gold-standard-100-whey-protein-powder-eu?variant=52105832956171",
        "selectors": { "price": ".product-price" },
        "fixed_name": "Gold Standard 100% Whey",
        "default_purity": 79,
        "fixed_weight": 0.9,
        "local_image": "img/on.jpg",
        "affiliate_link": None
    },
    {
        "brand": "BioTechUSA",
        "url": "https://shop.biotechusa.es/products/protein-power-1000-g", 
        "selectors": { "price": "#ProductPrice" },
        "fixed_name": "Protein Power",
        "default_purity": 86,
        "fixed_weight": 1.0,
        "local_image": "img/biotech.jpg",
        "affiliate_link": None
    }
]

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    return uc.Chrome(options=options, version_main=144)

def clean_price(price_text):
    if not price_text: return None
    if isinstance(price_text, (int, float)): return float(price_text)
    
    match = re.search(r'(\d+[\.,]\d+)', str(price_text))
    if match:
        clean = match.group(1).replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None
    return None

def extract_from_json_ld(driver):
    try:
        scripts = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
        for script in scripts:
            try:
                data = json.loads(script.get_attribute('innerHTML'))
                
                if isinstance(data, list):
                    data = data[0]
                
                if 'offers' in data:
                    offer = data['offers']
                    if isinstance(offer, list): offer = offer[0]
                    if 'price' in offer:
                        return offer['price']
                
                if 'price' in data:
                    return data['price']
                    
            except:
                continue
    except:
        pass
    return None

def extract_from_meta(driver):
    metas = [
        "product:price:amount",
        "og:price:amount",
        "price",
        "twitter:data1"
    ]
    for m in metas:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, f"meta[property='{m}'], meta[name='{m}']")
            content = elem.get_attribute("content")
            if content: return content
        except:
            continue
    return None

def scrape_site(driver, target):
    print(f"[*] {target['brand']} ({target['fixed_weight']}kg)...")
    try:
        driver.get(target['url'])
        time.sleep(random.uniform(5, 8))
        
        raw_price = None

        raw_price = extract_from_json_ld(driver)
        if raw_price:
            print(f"   -> (Fuente: JSON-LD) {raw_price}")

        if not raw_price:
            raw_price = extract_from_meta(driver)
            if raw_price:
                print(f"   -> (Fuente: META) {raw_price}")

        if not raw_price:
            try:
                wait = WebDriverWait(driver, 10)
                price_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
                raw_price = price_elem.text
                if not raw_price:
                    raw_price = price_elem.get_attribute("content")
                print(f"   -> (Fuente: CSS) {raw_price}")
            except:
                pass

        price = clean_price(raw_price)
        
        if price:
            print(f"   -> OK: {price}€")
            return {
                "id": target['brand'].lower().replace(" ", "_"),
                "brand": target['brand'],
                "name": target['fixed_name'],
                "price": price,
                "image": target['local_image'],
                "weight_kg": target['fixed_weight'],
                "protein_percent": target['default_purity'],
                "link": target.get('affiliate_link') or target['url'],
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        else:
            print(f"   -> FALLO: No se encontró precio. Guardando captura de error...")
            driver.save_screenshot(f"error_{target['brand']}.png")
            return None

    except Exception as e:
        print(f"   -> CRASH: {str(e)}")
        return None

def main():
    print("--- SCRAPER V4 (Modo Sigiloso + JSON-LD) ---")
    try:
        driver = get_driver()
    except Exception as e:
        print(f"Error iniciando Chrome: {e}")
        return

    results = []
    
    for target in TARGETS:
        data = scrape_site(driver, target)
        if data:
            results.append(data)
    
    driver.quit()
    
    if results:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print("\n[V] EXITO: DB Actualizada.")
    else:
        print("\n[X] FALLO TOTAL. Revisa las capturas .png generadas.")

if __name__ == "__main__":
    main()