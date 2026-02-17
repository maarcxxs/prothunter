import json
import time
import random
import re
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN MAESTRA ---
# Aquí definimos TODO lo estático para que el bot solo busque el precio.
TARGETS = [
    {
        "brand": "MyProtein",
        "url": "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
        "selectors": { "price": ".price-with-discounts" },
        "fixed_name": "Impact Whey Protein",
        "default_purity": 72,
        "fixed_weight": 1.0,
        "local_image": "img/myprotein.jpg",
        "affiliate_link": None # Pon aquí tu link cuando lo tengas
    },
    {
        "brand": "HSN",
        "url": "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0",
        "selectors": { "price": ".price-container .price" },
        "fixed_name": "Evowhey Protein 2.0",
        "default_purity": 78,
        "fixed_weight": 0.5, # HSN carga 500g por defecto
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
        "url": "https://www.optimumnutrition.com/es-es/Products/Protein/Shakes-%26-Powders/Gold-Standard-100%25-Whey-Protein/p/gold-standard-100-whey-protein",
        "selectors": { "price": ".product-price" },
        "fixed_name": "Gold Standard 100% Whey",
        "default_purity": 79,
        "fixed_weight": 0.9,
        "local_image": "img/on.jpg",
        "affiliate_link": None
    },
    {
        "brand": "BioTechUSA",
        "url": "https://shop.biotechusa.es/products/iso-whey-zero-500-g",
        "selectors": { "price": "#ProductPrice" },
        "fixed_name": "Iso Whey Zero",
        "default_purity": 84,
        "fixed_weight": 0.5,
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
    # Forzamos la versión 144 para sincronizar con GitHub Actions
    return uc.Chrome(options=options, version_main=144)

def clean_price(price_text):
    if not price_text: return None
    # Regex para buscar números decimales (ej: 31,99 o 31.99)
    match = re.search(r'(\d+[\.,]\d+)', price_text)
    if match:
        clean = match.group(1).replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None
    return None

def scrape_site(driver, target):
    print(f"[*] {target['brand']} ({target['fixed_weight']}kg)...")
    try:
        driver.get(target['url'])
        
        # Scroll táctico para activar carga perezosa (lazy load)
        driver.execute_script("window.scrollTo(0, 700);")
        time.sleep(random.uniform(4, 7))
        
        wait = WebDriverWait(driver, 20)
        
        # 1. EXTRACCIÓN DEL PRECIO (Lo único variable)
        try:
            price_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
            raw_price = price_elem.text
            # Si el texto está vacío, miramos atributos ocultos
            if not raw_price:
                raw_price = price_elem.get_attribute("content") or ""
        except:
            print(f"   -> Error: No se encontró el precio con {target['selectors']['price']}")
            return None

        # 2. LIMPIEZA
        price = clean_price(raw_price)
        
        if price:
            print(f"   -> OK: {price}€")
            return {
                "id": target['brand'].lower().replace(" ", "_"),
                "brand": target['brand'],
                "name": target['fixed_name'], # Usamos el nombre fijo config
                "price": price,
                "image": target['local_image'], # Usamos la ruta local config
                "weight_kg": target['fixed_weight'],
                "protein_percent": target['default_purity'],
                "link": target.get('affiliate_link') or target['url'],
                "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        else:
            print(f"   -> ERROR: Precio sucio '{raw_price}'")
            return None

    except Exception as e:
        print(f"   -> CRASH: {str(e)}")
        return None

def main():
    print("--- SCRAPER V3 (Optimizado: Imágenes y Nombres Locales) ---")
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
        print("\n[V] EXITO: Base de datos actualizada.")
    else:
        print("\n[X] FALLO: No se han guardado datos.")

if __name__ == "__main__":
    main()