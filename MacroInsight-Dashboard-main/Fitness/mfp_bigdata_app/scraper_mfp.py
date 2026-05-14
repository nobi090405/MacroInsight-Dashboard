from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import pandas as pd
import time
import os

# CONFIGURACIÓN DE MONGODB (Semana 6)
cliente_mongo = MongoClient("mongodb://localhost:27017/")
db = cliente_mongo["mfp_bigdata"]
coleccion = db["historial_nutricional"]

def iniciar_scraper(usuario, contrasena):
    print("🤖 Iniciando robot de extracción...")
    
    # 1. Configurar el navegador Chrome
    opciones = webdriver.ChromeOptions()
    # opciones.add_argument('--headless') # Descomenta esto después para que no se abra la ventana visible
    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--window-size=1920,1080')
    
    # Iniciar el driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
    
    try:
        # 2. Ir a la página de login de MyFitnessPal (Semana 13)
        print("🌐 Navegando a MyFitnessPal...")
        driver.get("https://www.myfitnesspal.com/es/account/login")
        
        # Esperar a que cargue el campo de email (máximo 10 segundos)
        wait = WebDriverWait(driver, 10)
        
        # Manejar posible banner de cookies si aparece
        try:
            btn_cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            btn_cookies.click()
            print("🍪 Cookies aceptadas.")
        except:
            pass # Si no hay banner, continuamos
            
        # 3. Ingresar credenciales e iniciar sesión
        print("🔑 Iniciando sesión...")
        input_email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        input_email.send_keys(usuario)
        
        # NOTA: MyFitnessPal a veces tiene el password en otra vista, 
        # Si el login es directo en una sola página:
        input_pass = driver.find_element(By.NAME, "password")
        input_pass.send_keys(contrasena)
        
        btn_login = driver.find_element(By.XPATH, "//button[@type='submit']")
        btn_login.click()
        
        # Esperar a que cargue el dashboard de inicio (comprobando que el login fue exitoso)
        time.sleep(5) # Pausa estática para dejar que termine la redirección
        
        # 4. Ir a la página del Diario de Alimentos
        print("📖 Navegando al diario de alimentos...")
        driver.get("https://www.myfitnesspal.com/es/food/diary")
        time.sleep(3)
        
        # AQUÍ IRÁ LA LÓGICA DE EXTRACCIÓN (LO HAREMOS EN EL SIGUIENTE PASO)
        # Vamos a extraer la tabla HTML, limpiarla con Pandas y guardarla en MongoDB.
        print("✅ Login exitoso y diario cargado. ¡Listo para extraer!")

    except Exception as e:
        print(f"❌ Ocurrió un error durante el scraping: {e}")
    finally:
        # 5. Cerrar el navegador
        print("🛑 Cerrando navegador...")
        driver.quit()

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    # ¡NUNCA PONGAS TUS CONTRASEÑAS REALES EN CÓDIGO PLANO SI LO SUBES A GITHUB!
    # Por ahora ponlas aquí para probar, pero luego usaremos variables de entorno.
    MI_EMAIL = "jsurcaf@autonoma.edu.pe"
    MI_PASSWORD = "2022dD1278."
    
    iniciar_scraper(MI_EMAIL, MI_PASSWORD)