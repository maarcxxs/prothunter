import json
import time
import random
import re
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN ---
TARGETS = [
    {
        "brand": "MyProtein",
        "url": "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
        "selectors": { "price": ".productPrice, .price, [data-test='product-price']" },
        "fixed_name": "Impact Whey Protein",
        "default_purity": 72,
        "fixed_weight": 1.0,
        "local_image": "img/myprotein.jpg",
        "affiliate_link": None
    },
    {
        "brand": "HSN",
        "url": "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0",
        "selectors": { "price": ".price-container .price, .product-price-primary" },
        "fixed_name": "Evowhey Protein 2.0",
        "default_purity": 78,
        "fixed_weight": 0.5,
        "local_image": "img/hsn.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Prozis",
        "url": "https://www.prozis.com/es/es/prozis/100-real-whey-protein-1000-g",
        "selectors": { "price": ".final-price, p.price, .selling-price, .product-price" },
        "fixed_name": "100% Real Whey Protein",
        "default_purity": 80,
        "fixed_weight": 1.0,
        "local_image": "img/prozis.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Optimum Nutrition",
        "url": "https://www.masmusculo.com/es/optimum-nutrition/100-whey-gold-standard-2lb-09kg-74210.html#/510-sabor-neutro",
        "selectors": { "price": ".product-price, span[data-testid='product-price']" },
        "fixed_name": "Gold Standard 100% Whey",
        "default_purity": 79,
        "fixed_weight": 0.9,
        "local_image": "img/on.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Iron Addict Labs",
        "url": "https://www.masmusculo.com/es/iron-addict-labs/addict-whey-2-kg-9214.html#/270-sabor-frutas_del_bosque",
        "selectors": { "price": ".product-price, span[data-testid='product-price']" },
        "fixed_name": "Addict Whey - 2KG",
        "default_purity": 73,
        "fixed_weight": 2.0,
        "local_image": "img/iron.jpg",
        "affiliate_link": None
    },
    {
        "brand": "BioTechUSA",
        "url": "https://shop.biotechusa.es/products/protein-power-1000-g", 
        "selectors": { "price": "#ProductPrice, .product-single__price" },
        "fixed_name": "Protein Power",
        "default_purity": 86,
        "fixed_weight": 1.0,
        "local_image": "img/biotech.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Decathlon",
        "url": "https://www.decathlon.es/es/p/whey-protein-sabor-neutro-900g/339696/g77m8756406",
        "selectors": { "price": ".prc__active-price" }, # Decathlon usa esta clase rara
        "fixed_name": "WHEY PROTEIN SABOR NEUTRO 900g",
        "default_purity": 75,
        "fixed_weight": 0.9,
        "local_image": "img/decathlon.jpg",
        "affiliate_link": None
    }
]

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Evita detección básica
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # HÍBRIDO: Detecta si es GitHub Actions (Linux) o Tu PC (Windows)
    if os.name == 'posix': 
        print("--- MODO SERVIDOR (Linux) ---")
        options.add_argument('--headless=new') 
        return uc.Chrome(options=options, version_main=144)
    else: 
        print("--- MODO LOCAL (Windows) ---")
        # En tu PC no forzamos versión para evitar conflictos
        return uc.Chrome(options=options)

def clean_price(price_text):
    if not price_text: return None
    # Busca patrón XX.XX o XX,XX
    match = re.search(r'(\d+[\.,]\d{2})', str(price_text))
    if match:
        clean = match.group(1).replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None
    return None

def handle_popups(driver):
    """ Intenta cerrar cookies y popups pulsando ESC y buscando botones """
    try:
        # 1. Truco del Ingeniero: Pulsar ESC cierra la mayoría de modales
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        
        # 2. Buscar botones de cookies agresivamente
        buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceptar') or contains(., 'Accept') or contains(., 'Consent')]")
        if buttons:
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print("   [!] Cookie/Popup aplastado.")
                    break
    except:
        pass

def scrape_site(driver, target):
    print(f"[*] {target['brand']}...")
    try:
        driver.get(target['url'])
        time.sleep(random.uniform(3, 5))
        
        # FASE 1: Limpieza
        handle_popups(driver)
        driver.execute_script("window.scrollTo(0, 500);") # Scroll para despertar la web

        raw_price = None

        # FASE 2: Búsqueda por Selectores CSS (La forma elegante)
        try:
            wait = WebDriverWait(driver, 5)
            price_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
            raw_price = price_elem.text
            print(f"   -> (CSS) Encontrado: {raw_price}")
        except:
            print("   -> (CSS) Falló el selector principal.")

        # FASE 3: Búsqueda por "Fuerza Bruta" (Regex en todo el HTML)
        # Si falló lo anterior, buscamos patrones de dinero en toda la página visible
        if not clean_price(raw_price):
            print("   -> (!) Activando modo Fuerza Bruta...")
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                # Busca precios aislados. Ej: "31,99 €" o "€31.99"
                prices = re.findall(r'(\d+[\.,]\d{2})\s?€|€\s?(\d+[\.,]\d{2})', body_text)
                
                # Cogemos el primer precio que parezca lógico (a veces pilla fechas o teléfonos)
                for p in prices:
                    p_val = p[0] if p[0] else p[1]
                    val = clean_price(p_val)
                    if val and 10 < val < 100: # Filtro de sentido común (entre 10€ y 100€)
                        raw_price = p_val
                        print(f"   -> (Fuerza Bruta) Encontrado posible precio: {raw_price}")
                        break
            except Exception as e:
                print(f"   -> Error en fuerza bruta: {e}")

        # PROCESADO FINAL
        price = clean_price(raw_price)
        
        if price:
            print(f"   -> ÉXITO: {price}€")
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
            print(f"   -> FALLO: Guardando captura...")
            driver.save_screenshot(f"error_{target['brand']}.png")
            return None

    except Exception as e:
        print(f"   -> CRASH: {str(e)}")
        driver.save_screenshot(f"crash_{target['brand']}.png")
        return None

def main():
    print("--- SCRAPER V5 (Modo Combate) ---")
    try:
        driver = get_driver()
    except Exception as e:
        print(f"Error crítico iniciando Chrome: {e}")
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
        print("\n[V] DB ACTUALIZADA.")
    else:
        print("\n[X] NO SE OBTUVIERON DATOS.")

if __name__ == "__main__":
    main()