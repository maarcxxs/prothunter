import json
import time
import random
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGETS = [
    {
        "brand": "MyProtein",
        "url": "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
        "selectors": {
            "price": ".price-with-discounts .price", 
            "name": "h1.productName_title",
            "image": ".productImage_image"
        },
        "default_purity": 72,
        "fixed_weight": 1.0  
    },
    {
        "brand": "HSN",
        "url": "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0",
        "selectors": {
            "price": ".final-price",
            "name": ".product-name h1",
            "image": "#MagicZoomProductMain img"
        },
        "default_purity": 78,
        "fixed_weight": 2.0 
    },
    {
        "brand": "Prozis",
        "url": "https://www.prozis.com/es/es/prozis/100-real-whey-protein-1000-g?label=TlVUMDAvMTQxNzY1MDE2Mg%3D%3D",
        "selectors": {
            "price": ".final-price",
            "name": ".product-name",
            "image": ".product-image img"
        },
        "default_purity": 80,
        "fixed_weight": 1.0
    },
    {
        "brand": "Biotech USA",
        "url": "https://shop.biotechusa.es/products/protein-power-1000-g",
        "selectors": {
            "price": ".np-product__price",
            "name": "#productTitle",
            "image": ".np__slide_img"
        },
        "default_purity": 86,
        "fixed_weight": 1.0
    },
    {
        "brand": "Optimum Nutrition",
        "url": "https://www.optimumnutrition.com/products/gold-standard-100-whey-protein-powder-eu?variant=52105832956171",
        "selectors": {
            "price": ".product-info__price sale-price", 
            "name": ".product-info__title h2",
            "image": ".product-gallery__media snap-center is-selected"
        },
        "default_purity": 80, #informar en la web que 80 tiene la de sin sabor, el resto cambia dependiendo del sabor
        "fixed_weight": 0.9 
    }
]

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new') 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options, version_main=144)

def clean_price(price_text):
    """Limpia el texto 'Desde 34,99 €' para dejar el float 34.99"""
    try:
        clean = price_text.replace("€", "").replace("From", "").replace("Desde", "").strip()
        clean = clean.replace(",", ".")
        return float(clean)
    except ValueError:
        return None

def scrape_site(driver, target):
    print(f"[*] Analizando {target['brand']} ({target['fixed_weight']}kg)...")
    try:
        driver.get(target['url'])
        time.sleep(random.uniform(3, 6))
        
        wait = WebDriverWait(driver, 15)
        
        price_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
        raw_price = price_elem.text
        
        try:
            name = driver.find_element(By.CSS_SELECTOR, target['selectors']['name']).text
        except:
            name = f"{target['brand']} Whey Protein"

        try:
            image_url = driver.find_element(By.CSS_SELECTOR, target['selectors']['image']).get_attribute("src")
        except:
            image_url = "img/whey-protein.jpg"

        price = clean_price(raw_price)
        
        if price:
            print(f"   -> PRECIO ENCONTRADO: {price}€")
            return {
                "id": target['brand'].lower().replace(" ", "_"),
                "brand": target['brand'],
                "name": name,
                "price": price,
                "image": image_url,
                "weight_kg": target['fixed_weight'], 
                "protein_percent": target['default_purity'],
                "link": target['url'], # afiliacion en el futuro
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        else:
            print(f"   -> ERROR: No se pudo limpiar el precio '{raw_price}'")
            return None

    except Exception as e:
        print(f"   -> FALLO CRÍTICO en {target['brand']}: {str(e)}")
        return None

def main():
    print("--- INICIANDO PROTHUNTER SCRAPER ---")
    driver = get_driver()
    results = []
    
    for target in TARGETS:
        data = scrape_site(driver, target)
        if data:
            results.append(data)
    
    driver.quit()

    if results:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print("\n[V] EXITO: Base de datos actualizada en data.json")
    else:
        print("\n[X] FRACASO: No se han extraído datos. Revisa selectores.")

if __name__ == "__main__":
    main()