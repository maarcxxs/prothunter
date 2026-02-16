import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver():
    options = Options()
    options.add_argument("--headless") # OBLIGATORIO para servidores sin pantalla
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # User Agent para no parecer un robot cutre
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    return webdriver.Chrome(options=options)

def scrape_myprotein(url):
    driver = get_driver()
    product_data = {}
    
    
    print(f"Escaneando: {url}")
    try:
        driver.get(url)
        # Esperamos a que cargue el precio (máx 10 seg)
        wait = WebDriverWait(driver, 10)
        
        # --- SELECTORES REALES MYPROTEIN (Pueden variar) ---
        
        # 1. Nombre del producto
        title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.productName_title")))
        product_data['name'] = title_elem.text

        # 2. Precio (Suelen tener la clase 'productPrice_price' o similar)
        # Buscamos algo que contenga el símbolo €
        price_elem = driver.find_element(By.CSS_SELECTOR, ".productPrice_price") 
        raw_price = price_elem.text.replace("€", "").replace(",", ".").strip()
        product_data['price'] = float(raw_price)

        # 3. Imagen
        img_elem = driver.find_element(By.CSS_SELECTOR, ".productImage_image")
        product_data['image'] = img_elem.get_attribute("src")
        
        # Datos estáticos (difíciles de sacar sin IA, los ponemos fijos por ahora)
        product_data['brand'] = "MyProtein"
        product_data['type'] = "whey" 
        product_data['weight_kg'] = 1.0 # Asumimos 1kg para simplificar el MVP
        product_data['protein_percent'] = 72 # Estándar de Impact Whey

        product_data['link'] = url # Tu enlace de afiliado iría aquí

        print(f"Éxito: {product_data['name']} - {product_data['price']}€")
        
    except Exception as e:
        print(f"Error en {url}: {e}")
        product_data = None
    finally:
        driver.quit()
        
    return product_data

# --- LISTA DE PRODUCTOS ---
urls = [
    "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html",
    # Añade más aquí...
]

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    results = []
    for url in urls:
        data = scrape_myprotein(url)
        if data:
            results.append(data)
            time.sleep(random.uniform(2, 5)) # Pausa ética
    
    # Guardar JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)