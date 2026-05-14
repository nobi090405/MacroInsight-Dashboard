from pymongo import MongoClient

# Pega tu cadena de conexión exacta aquí
URI = "mongodb+srv://usuario_pyspark:ZqCviyaeG43jVucq@cluster0.vytpge5.mongodb.net/historial_nutricional?appName=Cluster0"

try:
    # Intentamos conectarnos a la nube
    client = MongoClient(URI)
    
    # Hacemos un "ping" rápido para confirmar que responde
    client.admin.command('ping')
    
    print("✅ ¡BINGO! Conexión a MongoDB Atlas exitosa. Tu base de datos ya está en la nube ☁️")
except Exception as e:
    print(f"❌ Vaya, hubo un error de conexión: {e}")