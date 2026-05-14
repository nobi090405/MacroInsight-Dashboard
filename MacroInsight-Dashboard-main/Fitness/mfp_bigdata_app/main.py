import streamlit as st
import plotly.express as px
import streamlit as st
import plotly.express as px

# Importar nuestros módulos personalizados
from data_manager import get_spark_session, load_data
from ml_predictor import run_spark_prediction
from ai_assistant import generate_nutritional_insight

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="MacroInsight - Salud Pública", page_icon="🚀", layout="wide")

# ==========================================
# CARGAR ESTILOS CSS EXTERNOS
# ==========================================
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo {file_name}. Usando tema por defecto.")

# Aplicar diseño
load_css("style.css")

# Inicializar recursos
spark = get_spark_session()

# Importar nuestros módulos personalizados
from data_manager import get_spark_session, load_data, registrar_usuario_sistema, autenticar_usuario
from ml_predictor import run_spark_prediction
from ai_assistant import generate_nutritional_insight

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="MacroInsight - Salud Pública", page_icon="🚀", layout="wide")

def load_css(file_name):
    # ... (Tu código load_css se queda exactamente igual) ...
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo {file_name}. Usando tema por defecto.")

load_css("style.css")

# ==========================================
# 🔐 SISTEMA DE AUTENTICACIÓN (LOGIN/REGISTRO)
# ==========================================
# Inicializar variables de sesión si no existen
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.rol = ""

# Si NO está logueado, mostrar pantalla de acceso y DETENER la app
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso al Sistema MacroInsight</h1>", unsafe_allow_html=True)
    
    # Creamos dos pestañas para el Login
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrar Nuevo Personal"])
    
    with tab_login:
        with st.form("form_login"):
            st.subheader("Ingreso de Personal Autorizado")
            log_user = st.text_input("Usuario")
            log_pass = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                exito, rol = autenticar_usuario(log_user, log_pass)
                if exito:
                    st.session_state.logged_in = True
                    st.session_state.username = log_user
                    st.session_state.rol = rol
                    st.rerun() # Recarga la página para entrar al dashboard
                else:
                    st.error("❌ Credenciales incorrectas.")
                    
    with tab_registro:
        with st.form("form_registro"):
            st.subheader("Alta de Sistema")
            reg_user = st.text_input("Crear Usuario")
            reg_pass = st.text_input("Crear Contraseña", type="password")
            reg_rol = st.selectbox("Rol del Usuario", ["Nutricionista", "Gobierno (Salud Pública)"])
            submit_reg = st.form_submit_button("Registrar")
            
            if submit_reg:
                if reg_user and reg_pass:
                    exito, mensaje = registrar_usuario_sistema(reg_user, reg_pass, reg_rol)
                    if exito: st.success(mensaje)
                    else: st.error(mensaje)
                else:
                    st.warning("⚠️ Completa todos los campos.")
                    
    # st.stop() es clave: impide que el dashboard cargue si no hay sesión
    st.stop()

# ==========================================
# 🚀 A PARTIR DE AQUÍ COMIENZA TU DASHBOARD ORIGINAL
# ==========================================

# Inicializar recursos
spark = get_spark_session()
df = load_data()

if df.empty:
    st.error("No se encontraron datos en MongoDB. Revisa que Compass esté corriendo.")
    st.stop()

# --- BARRA LATERAL MODIFICADA PARA INCLUIR EL CERRAR SESIÓN ---
with st.sidebar:
    st.markdown("## 🚀 MacroInsight AI")
    st.caption("Analítica Predictiva a Gran Escala")
    
    # === MOSTRAR QUIÉN ESTÁ LOGUEADO ===
    st.success(f"👤 **{st.session_state.username}**")
    st.caption(f"🛡️ Perfil: {st.session_state.rol}")
    
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider() 
    
    # ... (El resto de tu Sidebar y Dashboard de main.py continúa exactamente igual) ...
    # st.header("🔍 Buscador de Pacientes")
    # lista_dnis = df['dni'].unique().tolist()
    # ...
df = load_data()

if df.empty:
    st.error("No se encontraron datos en MongoDB. Revisa que Compass esté corriendo.")
    st.stop()

# ==========================================
# BARRA LATERAL (SIDEBAR) - BUSCADOR POR DNI
# ==========================================
with st.sidebar:
    st.markdown("## 🚀 MacroInsight AI")
    st.caption("Analítica Predictiva a Gran Escala")
    st.divider() 
    
    st.header("🔍 Buscador de Pacientes")
    
    ##### CAMBIO AQUÍ: Usamos la columna 'dni' en lugar de 'user_id' #####
    lista_dnis = df['dni'].unique().tolist()
    
    selected_dni = st.selectbox(
        "🪪 Ingrese DNI del Ciudadano:",
        options=lista_dnis, 
        help="Seleccione el DNI de 8 dígitos para ver el historial clínico-ambiental."
    )
    
    st.divider()
    
    # Panel de Estado del Sistema 
    st.markdown("### 📡 Estado del Sistema")
    st.success("✅ Modelo Spark MLlib: Activo")
    st.success("✅ IA Asistente: Conectada")
    st.info("ℹ️ Datos actualizados a la Semana 12")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.caption("Desarrollado para el Proyecto Final de Big Data.")

# --- PROCESAMIENTO DEL PACIENTE SELECCIONADO ---
##### CAMBIO AQUÍ: Filtramos por la columna 'dni' #####
df_user = df[df['dni'] == selected_dni].copy()

# Opcional: recuperamos el ID original por si lo necesitas para algo interno
real_user_id = df_user['user_id'].iloc[0]

st.title(f"🚀 Plataforma Analítica - Paciente DNI: {selected_dni}")
st.caption(f"ID Técnico de Base de Datos: {real_user_id}")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard Histórico", "📈 Predicción (ML)", "🧠 Asistente Nutricional", "🌍 Análisis Global Poblacional"])

# ==========================================
# PESTAÑA 1, 2 y 3 (Se mantienen igual, ya usan df_user filtrado)
# ==========================================
with tab1:
    st.markdown("### Resumen de Consumo Histórico (Procesado con Spark SQL)")
    pdf_numeric = df_user[['total_kcal', 'total_prot', 'total_carbs', 'total_fat']].copy()
    spark_user_df = spark.createDataFrame(pdf_numeric)
    spark_user_df.createOrReplaceTempView("vista_nutricional")
    
    resultados_sql = spark.sql("""
        SELECT 
            AVG(total_kcal) as prom_kcal,
            AVG(total_prot) as prom_prot,
            AVG(total_carbs) as prom_carbs,
            AVG(total_fat) as prom_fat
        FROM vista_nutricional
    """).collect()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Promedio Kcal", f"{resultados_sql['prom_kcal']:.0f}")
    col2.metric("Promedio Prot (g)", f"{resultados_sql['prom_prot']:.0f}")
    col3.metric("Promedio Carbs (g)", f"{resultados_sql['prom_carbs']:.0f}")
    col4.metric("Promedio Grasas (g)", f"{resultados_sql['prom_fat']:.0f}")

    fig_line = px.line(df_user, x="date", y="total_kcal", title="Evolución Calórica Real", markers=True)
    st.plotly_chart(fig_line, width='stretch')

with tab2:
    st.markdown("### 📈 Predicción de Tendencia Calórica (Spark MLlib)")
    fig_pred, metric_or_error = run_spark_prediction(df_user, spark)
    
    if fig_pred is not None:
        st.plotly_chart(fig_pred, width='stretch')
        with st.expander("📝 Interpretación del Coach de Datos"):
            promedio = df_user['total_kcal'].mean()
            std_dev = df_user['total_kcal'].std()
            st.markdown(f"**Análisis de consistencia:** Tu variabilidad es de {std_dev:.0f} kcal.")
            st.write("La línea punteada muestra hacia dónde te diriges según el modelo de Big Data.")
        st.caption(f"Métricas del modelo (RMSE): {metric_or_error:.2f}")

with tab3:
    st.markdown("### 🧠 Panel de Control Nutricional (IA)")
    if st.button("Generar Análisis Nutricional"):
        with st.spinner("IA analizando datos..."):
            insight_text, error = generate_nutritional_insight(df_user)
            if error: st.error(error)
            else:
                partes = insight_text.split("|||")
                if len(partes) >= 4:
                    c1, c2 = st.columns(2)
                    with c1: st.info(partes[0])
                    with c2: st.success(partes[1])
                    c3, c4 = st.columns(2)
                    with c3: st.warning(partes[2])
                    with c4: st.help(partes[3])

# ==========================================
# PESTAÑA 4: ANÁLISIS GLOBAL (BIG DATA)
# ==========================================
with tab4:
    st.markdown("### 🌍 Perspectiva Poblacional")
    
    # --- GRÁFICO 3: Top Usuarios ---
    ##### CAMBIO AQUÍ: Usamos 'dni' para que el ranking muestre DNIs #####
    top_active = df['dni'].value_counts().head(10).reset_index()
    top_active.columns = ['DNI Paciente', 'Días Registrados']
    
    fig_bar = px.bar(
        top_active, 
        x='DNI Paciente', 
        y='Días Registrados', 
        title="Pacientes más Comprometidos con el Seguimiento",
        color='Días Registrados',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_bar, use_container_width=True)