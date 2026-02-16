import re
from utils.config import (
    PATRONES_PACIENTE, PROCEDIMIENTOS_KEYWORDS, MEDICAMENTOS_KEYWORDS,
    LABORATORIOS_KEYWORDS, IMAGENES_KEYWORDS, INTERCONSULTAS_KEYWORDS,
    PATRON_FECHA
)

def extraer_info_paciente(texto):
    """Extrae datos del paciente usando patrones predefinidos."""
    info = {}
    for clave, patron in PATRONES_PACIENTE.items():
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            info[clave] = match.group(1).strip()
    return info

def extraer_fechas_servicios(texto):
    """
    Busca menciones de servicios (hospitalización, UCI) con fechas asociadas.
    Retorna lista de diccionarios con 'servicio', 'fecha_ingreso', 'fecha_egreso' (si existe).
    """
    servicios_encontrados = []
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        if re.search(r'hospitalización|uci|cuidados intensivos', linea, re.IGNORECASE):
            # Buscar fechas en la misma línea o en las cercanas
            fechas = re.findall(PATRON_FECHA, linea)
            if fechas:
                # Asumir que la primera fecha es ingreso
                servicio = {
                    'servicio': linea.strip(),
                    'fecha_ingreso': fechas[0],
                    'fecha_egreso': fechas[1] if len(fechas) > 1 else None
                }
                servicios_encontrados.append(servicio)
    return servicios_encontrados

def extraer_procedimientos(texto):
    """Busca líneas que contengan palabras clave de procedimientos y extrae fecha si es posible."""
    procedimientos = []
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in PROCEDIMIENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fecha_match = re.search(PATRON_FECHA, linea)
                procedimientos.append({
                    'procedimiento': linea.strip(),
                    'fecha': fecha_match.group(0) if fecha_match else None
                })
                break  # Evitar duplicados por múltiples keywords
    return procedimientos

def extraer_medicamentos(texto):
    """Busca medicamentos por palabras clave, preferentemente en secciones de fórmula médica."""
    medicamentos = []
    # Primero, intentar acotar a secciones de fórmula médica si es posible
    # Por simplicidad, buscamos en todo el texto
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in MEDICAMENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fecha_match = re.search(PATRON_FECHA, linea)
                medicamentos.append({
                    'medicamento': linea.strip(),
                    'fecha': fecha_match.group(0) if fecha_match else None
                })
                break
    return medicamentos

def extraer_laboratorios(texto):
    """Extrae órdenes o resultados de laboratorio mencionados."""
    laboratorios = []
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in LABORATORIOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fecha_match = re.search(PATRON_FECHA, linea)
                laboratorios.append({
                    'examen': linea.strip(),
                    'fecha': fecha_match.group(0) if fecha_match else None
                })
                break
    return laboratorios

def extraer_imagenes(texto):
    """Extrae estudios de imágenes diagnósticas."""
    imagenes = []
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in IMAGENES_KEYWORDS:
            if kw.lower() in linea.lower():
                fecha_match = re.search(PATRON_FECHA, linea)
                imagenes.append({
                    'estudio': linea.strip(),
                    'fecha': fecha_match.group(0) if fecha_match else None
                })
                break
    return imagenes

def extraer_interconsultas(texto):
    """Extrae menciones de interconsultas o valoraciones por especialistas."""
    interconsultas = []
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in INTERCONSULTAS_KEYWORDS:
            if kw.lower() in linea.lower() and ('interconsulta' in linea.lower() or 'valoración' in linea.lower()):
                fecha_match = re.search(PATRON_FECHA, linea)
                interconsultas.append({
                    'especialidad': kw.capitalize(),
                    'descripcion': linea.strip(),
                    'fecha': fecha_match.group(0) if fecha_match else None
                })
                break
    return interconsultas
