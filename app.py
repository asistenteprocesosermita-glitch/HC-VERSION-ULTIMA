"""
Aplicación principal de Streamlit para extraer información facturable
de historias clínicas en PDF.
"""

import streamlit as st
import pandas as pd
import pdfplumber
import io
from datetime import datetime
from utils.extractor import extraer_todo, normalizar_texto, segmentar_por_secciones

# Configuración de la página
st.set_page_config(
    page_title="Facturación de Historias Clínicas",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("📄 Herramienta de extracción para facturación médica")
st.markdown("""
Esta aplicación permite cargar una historia clínica en formato PDF y extraer automáticamente
los elementos facturables: datos del paciente, estancias, procedimientos, medicamentos,
laboratorios, imágenes, interconsultas, transfusiones, soporte ventilatorio, notas de enfermería,
ordenamientos y evoluciones clave.
""")

# Inicializar variables de sesión para almacenar los datos editados
if 'datos_extraidos' not in st.session_state:
    st.session_state.datos_extraidos = None
if 'texto_completo' not in st.session_state:
    st.session_state.texto_completo = ""
if 'secciones' not in st.session_state:
    st.session_state.secciones = {}

# Barra lateral con instrucciones
with st.sidebar:
    st.header("Instrucciones")
    st.markdown("""
    1. Sube un archivo PDF de una historia clínica.
    2. La aplicación extraerá automáticamente la información.
    3. Revisa y edita los datos en cada pestaña.
    4. Exporta a Excel el resumen final.
    """)
    st.info("Los datos editables se guardan en la sesión actual. Al recargar la página se pierden.")
    st.warning("Para documentos escaneados (sin texto seleccionable), esta versión no puede extraer información. Se requiere OCR adicional.")

# Carga del archivo
uploaded_file = st.file_uploader("Selecciona el archivo PDF", type="pdf")

if uploaded_file is not None:
    # Botón para procesar (evita reprocesar cada vez que se interactúa)
    if st.button("Procesar PDF"):
        with st.spinner("Extrayendo texto del PDF..."):
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    texto_completo = ""
                    for pagina in pdf.pages:
                        contenido = pagina.extract_text()
                        if contenido:
                            texto_completo += contenido + "\n"
                if not texto_completo.strip():
                    st.error("No se pudo extraer texto. El archivo puede ser escaneado (requiere OCR).")
                    st.stop()
                st.session_state.texto_completo = texto_completo
                st.success(f"Texto extraído correctamente ({len(texto_completo)} caracteres).")
                
                # Procesar extracción
                with st.spinner("Analizando documento..."):
                    st.session_state.datos_extraidos = extraer_todo(texto_completo)
                    st.session_state.secciones = segmentar_por_secciones(texto_completo)
                st.success("Extracción completada.")
            except Exception as e:
                st.error(f"Error al leer el PDF: {e}")
                st.stop()

    # Si ya hay datos extraídos, mostramos las pestañas
    if st.session_state.datos_extraidos:
        datos = st.session_state.datos_extraidos
        
        # Crear pestañas para cada categoría
        tabs = st.tabs([
            "Paciente", "Estancias", "Procedimientos", "Medicamentos",
            "Laboratorios", "Imágenes", "Interconsultas", "Transfusiones",
            "Soporte Ventilatorio", "Notas Enfermería", "Ordenamientos Lab",
            "Evoluciones Clave", "Texto completo"
        ])
        
        # --- Pestaña Paciente ---
        with tabs[0]:
            st.subheader("Datos del paciente")
            if datos['paciente']:
                # Mostrar como JSON y permitir edición
                st.json(datos['paciente'])
                st.markdown("#### Editar datos del paciente")
                paciente_editado = {}
                cols = st.columns(2)
                items = list(datos['paciente'].items())
                for i, (k, v) in enumerate(items):
                    with cols[i % 2]:
                        paciente_editado[k] = st.text_input(f"{k.upper()}", value=v, key=f"paciente_{k}")
                if st.button("Guardar cambios de paciente"):
                    st.session_state.datos_extraidos['paciente'] = paciente_editado
                    st.success("Datos de paciente actualizados.")
            else:
                st.warning("No se encontraron datos del paciente.")
        
        # --- Pestaña Estancias ---
        with tabs[1]:
            st.subheader("Estancias por servicio")
            if datos['estancias']:
                df = pd.DataFrame(datos['estancias'])
                st.dataframe(df, use_container_width=True)
                st.caption("Eventos de ingreso/egreso detectados. Verifica que las fechas sean correctas.")
            else:
                st.info("No se detectaron estancias.")
        
        # --- Pestaña Procedimientos ---
        with tabs[2]:
            st.subheader("Procedimientos")
            if datos['procedimientos']:
                df = pd.DataFrame(datos['procedimientos'])
                edited_df = st.data_editor(df, num_rows="dynamic", key="proc_editor")
                if st.button("Guardar cambios de procedimientos"):
                    st.session_state.datos_extraidos['procedimientos'] = edited_df.to_dict('records')
                    st.success("Procedimientos actualizados.")
            else:
                st.info("No se detectaron procedimientos.")
        
        # --- Pestaña Medicamentos ---
        with tabs[3]:
            st.subheader("Medicamentos")
            if datos['medicamentos']:
                df = pd.DataFrame(datos['medicamentos'])
                edited_df = st.data_editor(df, num_rows="dynamic", key="med_editor")
                if st.button("Guardar cambios de medicamentos"):
                    st.session_state.datos_extraidos['medicamentos'] = edited_df.to_dict('records')
                    st.success("Medicamentos actualizados.")
            else:
                st.info("No se detectaron medicamentos.")
        
        # --- Pestaña Laboratorios ---
        with tabs[4]:
            st.subheader("Laboratorios")
            if datos['laboratorios']:
                df = pd.DataFrame(datos['laboratorios'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron laboratorios.")
        
        # --- Pestaña Imágenes ---
        with tabs[5]:
            st.subheader("Imágenes diagnósticas")
            if datos['imagenes']:
                df = pd.DataFrame(datos['imagenes'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron imágenes.")
        
        # --- Pestaña Interconsultas ---
        with tabs[6]:
            st.subheader("Interconsultas")
            if datos['interconsultas']:
                df = pd.DataFrame(datos['interconsultas'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron interconsultas.")
        
        # --- Pestaña Transfusiones ---
        with tabs[7]:
            st.subheader("Transfusiones")
            if datos['transfusiones']:
                df = pd.DataFrame(datos['transfusiones'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron transfusiones.")
        
        # --- Pestaña Soporte Ventilatorio ---
        with tabs[8]:
            st.subheader("Soporte ventilatorio")
            if datos['soporte_ventilatorio']:
                df = pd.DataFrame(datos['soporte_ventilatorio'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectó soporte ventilatorio.")
        
        # --- Pestaña Notas de Enfermería ---
        with tabs[9]:
            st.subheader("Notas de enfermería relevantes")
            if datos['notas_enfermeria']:
                df = pd.DataFrame(datos['notas_enfermeria'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron notas de enfermería relevantes.")
        
        # --- Pestaña Ordenamientos de Laboratorio ---
        with tabs[10]:
            st.subheader("Ordenamientos de laboratorio")
            if datos['ordenamientos_lab']:
                df = pd.DataFrame(datos['ordenamientos_lab'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron ordenamientos de laboratorio.")
        
        # --- Pestaña Evoluciones Clave ---
        with tabs[11]:
            st.subheader("Evoluciones clave (justificación clínica)")
            if datos['evoluciones_clave']:
                df = pd.DataFrame(datos['evoluciones_clave'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se detectaron evoluciones clave.")
        
        # --- Pestaña Texto completo ---
        with tabs[12]:
            st.subheader("Texto completo extraído")
            if st.session_state.texto_completo:
                st.text_area("Contenido del PDF", st.session_state.texto_completo, height=400)
                # Botón para copiar al portapapeles (usando st.code)
                with st.expander("Ver secciones detectadas"):
                    st.json(st.session_state.secciones)
            else:
                st.warning("No hay texto disponible.")
        
        # --- Botón de exportación a Excel (fuera de pestañas) ---
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Exportar todo a Excel", type="primary", use_container_width=True):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Función auxiliar para escribir DataFrame si hay datos
                    def escribir_hoja(nombre, datos):
                        if datos:
                            df = pd.DataFrame(datos)
                            df.to_excel(writer, sheet_name=nombre[:31], index=False)  # Límite de 31 caracteres
                    
                    escribir_hoja('Paciente', [datos['paciente']] if datos['paciente'] else None)
                    escribir_hoja('Estancias', datos['estancias'])
                    escribir_hoja('Procedimientos', datos['procedimientos'])
                    escribir_hoja('Medicamentos', datos['medicamentos'])
                    escribir_hoja('Laboratorios', datos['laboratorios'])
                    escribir_hoja('Imagenes', datos['imagenes'])
                    escribir_hoja('Interconsultas', datos['interconsultas'])
                    escribir_hoja('Transfusiones', datos['transfusiones'])
                    escribir_hoja('SoporteVentilatorio', datos['soporte_ventilatorio'])
                    escribir_hoja('NotasEnfermeria', datos['notas_enfermeria'])
                    escribir_hoja('OrdenamientosLab', datos['ordenamientos_lab'])
                    escribir_hoja('EvolucionesClave', datos['evoluciones_clave'])
                
                st.download_button(
                    label="Descargar archivo Excel",
                    data=output.getvalue(),
                    file_name=f"resumen_facturacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

else:
    # Mensaje inicial cuando no hay archivo
    st.info("👆 Sube un archivo PDF para comenzar.")
    
    # Ejemplo de cómo se vería la extracción (opcional)
    with st.expander("Ver ejemplo de estructura de datos extraídos"):
        st.code("""
{
  "paciente": {"cc": "73129351", "nombre": "JAVIER ENRIQUE MARRUGO RODRIGUEZ", ...},
  "estancias": [{"servicio": "Hospitalización General", "fecha": "30/10/2025", "hora": "05:38", "tipo": "ingreso"}, ...],
  "procedimientos": [{"procedimiento": "Biopsia de médula ósea", "fecha": "05/11/2025", ...}],
  "medicamentos": [{"medicamento": "Citarabina 172 mg IV cada 24h", "fecha": "22/11/2025", ...}],
  ...
}
        """)

# Pie de página
st.divider()
st.caption("Desarrollado para facturación de historias clínicas. Versión 1.0")
