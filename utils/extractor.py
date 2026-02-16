# utils/extractor.py - VERSIÓN MÍNIMA DE PRUEBA
def normalizar_texto(texto):
    return texto.strip() if texto else ""

def segmentar_por_secciones(texto):
    return {}

def extraer_todo(texto):
    return {
        'paciente': {},
        'estancias': [],
        'procedimientos': [],
        'medicamentos': [],
        'laboratorios': [],
        'imagenes': [],
        'interconsultas': [],
        'transfusiones': [],
        'soporte_ventilatorio': [],
        'notas_enfermeria': [],
        'ordenamientos_lab': [],
        'evoluciones_clave': []
    }
