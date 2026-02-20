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

# --- CONFIGURACIÓN DE OBJETIVOS ---
TARGETS = [
    {
        "brand": "MyProtein",
        "url": "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
        "selectors": { "price": ".productPrice, .price, [data-test='product-price']" },
        "fixed_name": "Impact Whey Protein 1KG",
        "default_purity": 72,
        "fixed_weight": 1.0,
        "local_image": "img/myprotein.jpg",
        "category": "protein",
        "affiliate_link": None
    },
    {
        "brand": "HSN",
        "url": "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0",
        "selectors": { "price": ".price-container .price, .product-price-primary" },
        "fixed_name": "Evowhey Protein 0,5KG",
        "default_purity": 78,
        "fixed_weight": 0.5,
        "local_image": "img/hsn.jpg",
        "category": "protein",
        "affiliate_link": None
    },
    {
        "brand": "HSN",
        "category": "creatina",
        "url": "https://www.hsnstore.com/marcas/raw-series/creatina-monohidrato-en-polvo",
        "selectors": { "price": ".product-price-primary, .buy-box .price, .product-buy-box .price, span[itemprop='price']" },
        "fixed_name": "Creatina Monohidrato en Polvo 150g",
        "default_purity": 100,
        "fixed_weight": 0.15,
        "local_image": "img/creatina_hsn.jpg",
        "affiliate_link": None
    },
    {
        "brand": "MyProtein",
        "category": "creatina",
        "url": "https://www.myprotein.es/p/nutricion-deportiva/creatina-monohidrato-en-polvo/10530050/?variation=10530054",
        "selectors": { "price": ".productPrice, .price, [data-test='product-price']" },
        "fixed_name": "Creatina Monohidrato 500g",
        "default_purity": 100,
        "fixed_weight": 0.5,
        "local_image": "img/creatina_mp.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Optimum Nutrition",
        "category": "protein",
        "url": "https://www.masmusculo.com/es/optimum-nutrition/100-whey-gold-standard-2lb-09kg-74210.html",
        "selectors": { "price": ".current-price span, #our_price_display, .price-sales, div.current-price" },
        "fixed_name": "Gold Standard 100% Whey",
        "default_purity": 79,
        "fixed_weight": 0.9,
        "local_image": "img/on.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Iron Addict Labs",
        "category": "protein",
        "url": "https://www.masmusculo.com/es/iron-addict-labs/addict-whey-2-kg-9214.html",
        "selectors": { "price": ".current-price span, #our_price_display, .price-sales, div.current-price" },
        "fixed_name": "Addict Whey - 2KG",
        "default_purity": 73,
        "fixed_weight": 2.0,
        "local_image": "img/iron.jpg",
        "affiliate_link": None
    },
    {
        "brand": "Prozis",
        "category": "protein",
        "url": "https://www.prozis.com/es/es/prozis/100-real-whey-protein-1000-g",
        "selectors": { 
            "price": "span.final-price, div[data-test='final-price'], span.selling-price" 
        },
        "fixed_name": "100% Real Whey Protein",
        "default_purity": 80,
        "fixed_weight": 1.0,
        "local_image": "img/prozis.jpg",
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
        "category": "protein",
        "affiliate_link": None
    },
    {
        "brand": "Decathlon",
        "url": "https://www.decathlon.es/es/p/whey-protein-sabor-neutro-900g/339696/g77m8756406",
        "selectors": { "price": ".vp-price-amount, .vp-price-amount--large" },
        "fixed_name": "WHEY PROTEIN 900g",
        "default_purity": 75,
        "fixed_weight": 0.9,
        "local_image": "img/decathlon.jpg",
        "category": "protein",
        "affiliate_link": None
    }
]

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # User Agent móvil para engañar a Prozis y webs difíciles
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

    if os.name == 'posix': 
        print("--- MODO SERVIDOR (Linux) ---")
        options.add_argument('--headless=new') 
        return uc.Chrome(options=options, version_main=144)
    else: 
        print("--- MODO LOCAL (Windows) ---")
        return uc.Chrome(options=options, version_main=145)

def clean_price(price_text):
    if not price_text: return None
    # Limpiamos símbolos raros y espacios
    clean_txt = str(price_text).replace('\xa0', '').replace('&nbsp;', '')
    
    # Busca patrón XX.XX o XX,XX
    match = re.search(r'(\d+[\.,]\d{2})', clean_txt)
    if match:
        clean = match.group(1).replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return None
    return None

def handle_popups(driver):
    try:
        # ESC para cerrar modales
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        # Click en botones de Cookies comunes
        buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aceptar') or contains(., 'Accept') or contains(., 'Consent')]")
        if buttons:
            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    break
    except:
        pass

def scrape_site(driver, target, max_retries=3):
    print(f"[*] {target['brand']}...")
    
    for attempt in range(max_retries):
        try:
            driver.get(target['url'])
            time.sleep(random.uniform(4, 7))
            handle_popups(driver)
            
            driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)

            raw_price = None

            try:
                wait = WebDriverWait(driver, 5)
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target['selectors']['price'])))
                
                raw_price = element.get_attribute("content")
                if not raw_price:
                    raw_price = element.text
                    
                print(f"   -> (CSS) Encontrado raw: {raw_price}")
            except:
                pass

            if not clean_price(raw_price):
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    prices = re.findall(r'(\d+[\.,]\d{2})\s?€|€\s?(\d+[\.,]\d{2})', body_text)
                    for p in prices:
                        p_val = p[0] if p[0] else p[1]
                        val = clean_price(p_val)
                        if val and 10 < val < 100:
                            raw_price = p_val
                            break
                except:
                    pass

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
                    "category": target['category'],
                    "link": target.get('affiliate_link') or target['url'],
                    "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
            else:
                print(f"   -> Intento {attempt + 1} fallido. Reintentando...")
                time.sleep(random.uniform(2, 5))
                if attempt == max_retries - 1:
                    driver.save_screenshot(f"error_{target['brand']}.png")
                    
        except Exception as e:
            print(f"   -> CRASH en intento {attempt + 1}: {str(e)}")
            time.sleep(random.uniform(2, 5))
            
    return None


def main():
    print("--- SCRAPER V6 ---")
    time.sleep(random.uniform(15, 60))
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
        print("\n[V] DB ACTUALIZADA.")
    else:
        print("\n[X] NO SE OBTUVIERON DATOS.")

if __name__ == "__main__":
    main()

