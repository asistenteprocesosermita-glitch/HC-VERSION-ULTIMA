import re
import pandas as pd

def extract_patient_info(text):
    """Extrae datos del paciente: CC, nombre, edad, EPS."""
    info = {}
    # Patrones (ajusta según el formato real de tus documentos)
    cc_match = re.search(r'No\.?\s*CC:\s*(\d+)', text, re.IGNORECASE)
    if cc_match:
        info['cc'] = cc_match.group(1)
    
    nombre_match = re.search(r'Nombre:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Edad|Fecha)', text, re.IGNORECASE)
    if nombre_match:
        info['nombre'] = nombre_match.group(1).strip()
    
    edad_match = re.search(r'Edad actual:\s*(\d+)', text, re.IGNORECASE)
    if edad_match:
        info['edad'] = edad_match.group(1)
    
    eps_match = re.search(r'Empresa:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if eps_match:
        info['eps'] = eps_match.group(1).strip()
    
    return info

def extract_admission_dates(text):
    """Extrae fechas de ingreso a cada servicio."""
    # Busca patrones como "INGRESO: 30/10/2025" o "Fecha de ingreso: ..."
    # Devuelve lista de diccionarios con servicio, fecha ingreso, fecha egreso
    admissions = []
    # Ejemplo simple: buscar "Hospitalización General" seguido de fecha
    pattern = r'(Hospitalización\s+General|UCI|Cuidados\s+Intensivos).*?(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        admissions.append({
            'servicio': match.group(1),
            'fecha': match.group(2),
            'hora': match.group(3)
        })
    # Luego habría que emparejar ingresos y egresos...
    return admissions

def extract_procedures(text):
    """Busca procedimientos (palabras clave como 'biopsia', 'catéter', etc.)"""
    keywords = ['biopsia', 'catéter', 'intubación', 'toracocentesis', 'transfusión', 
                'colocación de', 'ventilación mecánica', 'sonda']
    procedures = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        for kw in keywords:
            if kw.lower() in line.lower():
                # Intenta capturar fecha si está cerca
                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', line)
                fecha = date_match.group(1) if date_match else None
                procedures.append({
                    'procedimiento': line.strip(),
                    'fecha': fecha
                })
    return procedures

# ... más funciones para medicamentos, laboratorios, imágenes, etc.
