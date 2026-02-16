import streamlit as st
import pdfplumber
import pandas as pd
import io
from utils.extractor import (
    extraer_info_paciente, extraer_fechas_servicios,
    extraer_procedimientos, extraer_medicamentos,
    extraer_laboratorios, extraer_imagenes, extraer_interconsultas
)

st.set_page_config(page_title="Facturación de Historias Clínicas", layout="wide")
st.title("📄 Herramienta de extracción para facturación médica")
st.markdown("Sube una historia clínica en formato PDF para extraer automáticamente los elementos facturables.")

uploaded_file = st.file_uploader("Selecciona el archivo PDF", type="pdf")

if uploaded_file is not None:
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
        except Exception as e:
            st.error(f"Error al leer el PDF: {e}")
            st.stop()

    # Extraer información usando las funciones
    paciente = extraer_info_paciente(texto_completo)
    servicios = extraer_fechas_servicios(texto_completo)
    procedimientos = extraer_procedimientos(texto_completo)
    medicamentos = extraer_medicamentos(texto_completo)
    laboratorios = extraer_laboratorios(texto_completo)
    imagenes = extraer_imagenes(texto_completo)
    interconsultas = extraer_interconsultas(texto_completo)

    # Crear pestañas para mostrar resultados
    tabs = st.tabs([
        "Paciente", "Estancias", "Procedimientos", "Medicamentos",
        "Laboratorios", "Imágenes", "Interconsultas", "Texto completo"
    ])

    with tabs[0]:
        st.subheader("Datos del paciente")
        if paciente:
            st.json(paciente)
            # Permitir edición de datos del paciente
            st.subheader("Editar datos")
            paciente_editado = {}
            for k, v in paciente.items():
                paciente_editado[k] = st.text_input(f"{k.upper()}", value=v)
            if st.button("Guardar cambios de paciente"):
                st.session_state['paciente'] = paciente_editado
                st.success("Datos actualizados (solo en sesión actual)")
        else:
            st.warning("No se encontraron datos del paciente.")

    with tabs[1]:
        st.subheader("Estancias por servicio")
        if servicios:
            df_servicios = pd.DataFrame(servicios)
            st.dataframe(df_servicios, use_container_width=True)
        else:
            st.info("No se detectaron servicios de hospitalización.")

    with tabs[2]:
        st.subheader("Procedimientos identificados")
        if procedimientos:
            df_proc = pd.DataFrame(procedimientos)
            edited_proc = st.data_editor(df_proc, num_rows="dynamic", key="proc_editor")
            st.session_state['procedimientos'] = edited_proc
        else:
            st.info("No se encontraron procedimientos.")

    with tabs[3]:
        st.subheader("Medicamentos relevantes")
        if medicamentos:
            df_med = pd.DataFrame(medicamentos)
            edited_med = st.data_editor(df_med, num_rows="dynamic", key="med_editor")
            st.session_state['medicamentos'] = edited_med
        else:
            st.info("No se detectaron medicamentos.")

    with tabs[4]:
        st.subheader("Laboratorios")
        if laboratorios:
            df_lab = pd.DataFrame(laboratorios)
            st.dataframe(df_lab, use_container_width=True)
        else:
            st.info("No se encontraron exámenes de laboratorio.")

    with tabs[5]:
        st.subheader("Imágenes diagnósticas")
        if imagenes:
            df_img = pd.DataFrame(imagenes)
            st.dataframe(df_img, use_container_width=True)
        else:
            st.info("No se encontraron estudios de imagen.")

    with tabs[6]:
        st.subheader("Interconsultas")
        if interconsultas:
            df_int = pd.DataFrame(interconsultas)
            st.dataframe(df_int, use_container_width=True)
        else:
            st.info("No se encontraron interconsultas.")

    with tabs[7]:
        st.subheader("Texto extraído (primeros 3000 caracteres)")
        st.text(texto_completo[:3000] + ("..." if len(texto_completo) > 3000 else ""))

    # Botón para exportar todo a Excel
    if st.button("📥 Exportar a Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if paciente:
                pd.DataFrame([paciente]).to_excel(writer, sheet_name='Paciente', index=False)
            if servicios:
                pd.DataFrame(servicios).to_excel(writer, sheet_name='Estancias', index=False)
            if procedimientos:
                # Usar la versión editada si existe
                df_proc_exp = st.session_state.get('procedimientos', pd.DataFrame(procedimientos))
                df_proc_exp.to_excel(writer, sheet_name='Procedimientos', index=False)
            if medicamentos:
                df_med_exp = st.session_state.get('medicamentos', pd.DataFrame(medicamentos))
                df_med_exp.to_excel(writer, sheet_name='Medicamentos', index=False)
            if laboratorios:
                pd.DataFrame(laboratorios).to_excel(writer, sheet_name='Laboratorios', index=False)
            if imagenes:
                pd.DataFrame(imagenes).to_excel(writer, sheet_name='Imagenes', index=False)
            if interconsultas:
                pd.DataFrame(interconsultas).to_excel(writer, sheet_name='Interconsultas', index=False)
        st.download_button(
            label="Descargar archivo Excel",
            data=output.getvalue(),
            file_name="resumen_facturacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
