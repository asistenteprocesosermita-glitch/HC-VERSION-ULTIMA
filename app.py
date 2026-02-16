import streamlit as st
import pdfplumber
import pandas as pd
from utils.extractor import extract_patient_info, extract_admission_dates, extract_procedures
import io

st.set_page_config(page_title="Facturación HC", layout="wide")
st.title("📄 Extractor de información facturable de historias clínicas")

uploaded_file = st.file_uploader("Sube el archivo PDF de la historia clínica", type="pdf")

if uploaded_file is not None:
    # Extraer texto del PDF
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    if not text:
        st.error("No se pudo extraer texto del PDF. Puede ser un documento escaneado (requiere OCR).")
    else:
        st.success("Texto extraído correctamente. Procesando...")
        
        # Extraer información
        patient_info = extract_patient_info(text)
        admissions = extract_admission_dates(text)
        procedures = extract_procedures(text)
        
        # Mostrar resultados en pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["Paciente", "Estancias", "Procedimientos", "Texto completo"])
        
        with tab1:
            st.subheader("Datos del paciente")
            if patient_info:
                st.json(patient_info)
            else:
                st.warning("No se encontraron datos del paciente.")
        
        with tab2:
            st.subheader("Ingresos por servicio")
            if admissions:
                df_adm = pd.DataFrame(admissions)
                st.dataframe(df_adm)
            else:
                st.warning("No se encontraron fechas de ingreso.")
        
        with tab3:
            st.subheader("Procedimientos detectados")
            if procedures:
                df_proc = pd.DataFrame(procedures)
                st.dataframe(df_proc)
            else:
                st.warning("No se encontraron procedimientos.")
        
        with tab4:
            st.subheader("Texto completo extraído (primeros 2000 caracteres)")
            st.text(text[:2000] + "...")
        
        # Botón para exportar a Excel
        if st.button("Exportar resumen a Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if patient_info:
                    pd.DataFrame([patient_info]).to_excel(writer, sheet_name='Paciente', index=False)
                if admissions:
                    pd.DataFrame(admissions).to_excel(writer, sheet_name='Estancias', index=False)
                if procedures:
                    pd.DataFrame(procedures).to_excel(writer, sheet_name='Procedimientos', index=False)
            st.download_button(
                label="Descargar Excel",
                data=output.getvalue(),
                file_name="resumen_facturacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
