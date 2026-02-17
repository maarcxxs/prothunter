import json
import time
import random
import re  # <--- NUEVA LIBRERÍA IMPORTANTE
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
            "price": ".price-with-discounts", # Selector más amplio, la regex lo limpiará
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
            "price": ".price-container .price",
            "name": ".product-name h1",
            "image": ".product-image-photo" # Selector más limpio para la imagen
        },
        "default_purity": 78,
        "fixed_weight": 0.5 
    },
    {
        "brand": "Prozis",
        "url": "https://www.prozis.com/es/es/prozis/100-real-whey-protein-1000-g",
        "selectors": {
            # Selector actualizado para Prozis
            "price": "p.big-price", 
            "name": ".product-name",
            "image": ".product-image img"
        },
        "default_purity": 80,
        "fixed_weight": 1.0
    },
    {
        "brand": "Optimum Nutrition",
        "url": "https://www.optimumnutrition.com/es-es/Products/Protein/Shakes-%26-Powders/Gold-Standard-100%25-Whey-Protein/p/gold-standard-100-whey-protein",
        "selectors": {
            # Selector actualizado a uno más simple
            "price": ".product-price", 
            "name": "h1",
            "image": ".product-gallery__image"
        },
        "default_purity": 79,
        "fixed_weight": 0.9
    },
    {
        "brand": "BioTechUSA",
        "url": "https://shop.biotechusa.es/products/iso-whey-zero-500-g", 
        "selectors": {
            "price": "#ProductPrice",
            "name": "#productTitle",
            "image": "#bigpic"
        },
        "default_purity": 86,
        "fixed_weight": 1.0
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
    """
    Usa Expresiones Regulares (Regex) para encontrar el primer número decimal
    en medio de cualquier texto basura.
    """
    if not price_text: return None
    
    match = re.search(r'(\d+[\.,]\d+)', price_text)
    
    if match:
        clean = match.group(1)
        clean = clean.replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None
    return None

def scrape_site(driver, target):
    print(f"[*] Analizando {target['brand']} ({target['fixed_weight']}kg)...")
    try:
        driver.get(target['url'])
        time.sleep(random.uniform(3, 6))
        
        wait = WebDriverWait(driver, 20) 
        
    
        try:
            price_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
            raw_price = price_elem.text
           
            if not raw_price:
                raw_price = price_elem.get_attribute("content") or ""
        except:
            print(f"   -> No se encontró el selector de precio: {target['selectors']['price']}")
            return None
        
        
        try:
            name = driver.find_element(By.CSS_SELECTOR, target['selectors']['name']).text
        except:
            name = f"{target['brand']} Whey Protein"

       
        try:
            image_url = driver.find_element(By.CSS_SELECTOR, target['selectors']['image']).get_attribute("src")
        except:
            image_url = "img/placeholder.jpg"

        
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
                "link": target.get('affiliate_link', target['url']),
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        else:
            print(f"   -> ERROR: No se pudo extraer número de: '{raw_price}'")
            return None

    except Exception as e:
        print(f"   -> FALLO CRÍTICO en {target['brand']}: {str(e)}")
        return None

def main():
    print("--- INICIANDO PROTHUNTER SCRAPER V2 ---")
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
        print("\n[V] EXITO TOTAL: data.json actualizado.")
    else:
        print("\n[X] ALERTA: No se guardaron datos.")

if __name__ == "__main__":
    main()