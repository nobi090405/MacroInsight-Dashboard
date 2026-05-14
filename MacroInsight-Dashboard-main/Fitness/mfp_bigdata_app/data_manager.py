import pandas as pd
import os
import sys
import streamlit as st
from pymongo import MongoClient
from pyspark.sql import SparkSession
import hashlib

# Configuración de Spark para la nube
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# 1. CONEXIÓN OPTIMIZADA (Cacheamos el cliente para no saturar la base de datos)
@st.cache_resource
def get_mongo_client():
    try:
        # Usamos el secreto guardado en Streamlit Cloud
        uri = st.secrets["MONGO_URI"]
        return MongoClient(uri, serverSelectionTimeoutMS=5000)
    except Exception as e:
        st.error(f"❌ Error configurando el cliente de MongoDB: {e}")
        return None

@st.cache_resource
def get_spark_session():
    return SparkSession.builder \
        .appName("MFP_BigData_ML") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    client = get_mongo_client()
    if client is None:
        return pd.DataFrame()
        
    try:
        db = client["mfp_bigdata"]
        coleccion = db["historial_nutricional"]
        
        datos = list(coleccion.find())
        if not datos:
            st.warning("⚠️ No se encontraron datos en la colección 'historial_nutricional'.")
            return pd.DataFrame()
            
        df = pd.DataFrame(datos)
        
        # Limpieza
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['user_id', 'date']).sort_values('date')

        # Lógica de DNIs anónimos
        unique_users = df['user_id'].unique()
        dni_map = {uid: f"10{i+450280:06d}" for i, uid in enumerate(unique_users)}
        df['dni'] = df['user_id'].map(dni_map)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos de Atlas: {e}")
        return pd.DataFrame()

# 3. GESTIÓN DE USUARIOS
def encriptar_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario_sistema(username, password, rol):
    client = get_mongo_client()
    if client is None: return False, "Error de conexión"
    
    try:
        db = client["mfp_bigdata"]
        coleccion_usuarios = db["usuarios_sistema"]
        
        if coleccion_usuarios.find_one({"username": username}):
            return False, "❌ El nombre de usuario ya está en uso."
            
        nuevo_usuario = {
            "username": username,
            "password": encriptar_password(password),
            "rol": rol
        }
        coleccion_usuarios.insert_one(nuevo_usuario)
        return True, "✅ ¡Registro exitoso!"
    except Exception as e:
        return False, f"Error: {e}"

def autenticar_usuario(username, password):
    client = get_mongo_client()
    if client is None: return False, None
    
    try:
        db = client["mfp_bigdata"]
        coleccion_usuarios = db["usuarios_sistema"]
        
        # Buscamos el usuario
        user = coleccion_usuarios.find_one({
            "username": username, 
            "password": encriptar_password(password)
        })
        
        # Verificamos si existe antes de intentar acceder a ['rol']
        if user and "rol" in user:
            return True, user["rol"]
        return False, None
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
        return False, None
