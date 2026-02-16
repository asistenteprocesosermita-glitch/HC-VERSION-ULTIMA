import os
import sys
import streamlit as st
import pdfplumber
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Facturación HC", layout="wide")
st.title("📄 Extractor de información facturable (modo diagnóstico)")

# --- DIAGNÓSTICO DE LA ESTRUCTURA ---
utils_path = os.path.join(os.path.dirname(__file__), 'utils')
st.write("**Diagnóstico de carpetas:**")
st.write(f"Ruta de utils: {utils_path}")
if os.path.exists(utils_path):
    st.write("Contenido de utils:", os.listdir(utils_path))
else:
    st.error("La carpeta 'utils' NO existe en la raíz del proyecto.")

# --- INTENTO DE IMPORTACIÓN ---
try:
    from utils.extractor import extraer_todo, normalizar_texto, segmentar_por_secciones
    st.success("✅ Importación desde utils.extractor exitosa")
    IMPORT_OK = True
except ImportError as e:
    st.error(f"❌ Error importando desde utils.extractor: {e}")
    st.info("Intentando importar desde archivo en la raíz...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from extractor import extraer_todo, normalizar_texto, segmentar_por_secciones
        st.success("✅ Importación desde extractor (raíz) exitosa")
        IMPORT_OK = True
    except ImportError as e2:
        st.error(f"❌ También falló la importación desde raíz: {e2}")
        st.stop()

# --- RESTO DE LA APP (solo si la importación fue exitosa) ---
if IMPORT_OK:
    uploaded_file = st.file_uploader("Sube el archivo PDF de la historia clínica", type="pdf")
    if uploaded_file is not None:
        if st.button("Procesar PDF"):
            with st.spinner("Extrayendo texto..."):
                with pdfplumber.open(uploaded_file) as pdf:
                    texto = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            texto += page_text + "\n"
                if not texto.strip():
                    st.error("No se pudo extraer texto. El PDF puede ser escaneado.")
                else:
                    st.success("Texto extraído, ejecutando extracción...")
                    datos = extraer_todo(texto)
                    st.json(datos)  # Mostrar resultado
