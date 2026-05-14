import traceback
import streamlit as st
from google import genai

def generate_nutritional_insight(df_user):
    # Obtenemos la API key de los secretos de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    
    try:
        client = genai.Client(api_key=api_key)
        
        # 1. Extraemos la "radiografía" real y completa del usuario
        avg_kcal = df_user['total_kcal'].mean()
        avg_prot = df_user['total_prot'].mean()
        avg_carbs = df_user['total_carbs'].mean()
        avg_fat = df_user['total_fat'].mean() # Agregamos las grasas
        max_kcal = df_user['total_kcal'].max() # Agregamos el pico máximo
        
# 2. Creamos el súper-prompt con separadores para el Dashboard
        prompt = f"""
        Actúa como un Nutricionista Deportivo y Entrenador Personal de élite.
        Aquí tienes el promedio diario de consumo de mi cliente según su historial:
        - Calorías: {avg_kcal:.0f} kcal (Pico máximo: {max_kcal:.0f} kcal)
        - Proteínas: {avg_prot:.0f} g
        - Carbohidratos: {avg_carbs:.0f} g
        - Grasas: {avg_fat:.0f} g

        Tu tarea es generar 4 secciones de análisis. 
        REGLA DE ORO: Debes separar CADA SECCIÓN usando EXACTAMENTE estos 3 caracteres: |||
        No uses títulos con # para las secciones, yo los pondré en la interfaz visual. Solo dame el contenido.

        [Escribe aquí un saludo motivador y 3 viñetas con el veredicto general de sus hábitos]
        |||
        [Escribe aquí SOLO una TABLA en Markdown con 3 columnas: Nutriente, Tu Promedio, Veredicto del Coach. Analiza los 4 macros]
        |||
        [Escribe aquí SOLO una TABLA en Markdown con 3 columnas: Momento del día, Comida/Snack, Beneficio. Dame 3 ideas de snacks]
        |||
        [Escribe aquí un párrafo corto y potente recomendando un plan de entrenamiento físico adecuado a sus calorías]
        """
        
        # 3. Llamamos a Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text, None
        
    except Exception as e:
        error_msg = f"Vaya, parece que hay un problema: {e}"
        print("\n" + "="*60)
        print("❌ ERROR TÉCNICO DETECTADO:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        return None, error_msg