# Palabras clave para procedimientos
PROCEDURE_KEYWORDS = [
    'biopsia', 'catéter venoso central', 'intubación', 'toracocentesis',
    'transfusión de glóbulos rojos', 'transfusión de plaquetas',
    'ventilación mecánica', 'sonda vesical', 'sonda orogástrica',
    'colocación de', 'curación de catéter'
]

# Secciones del documento (para segmentar)
SECTIONS = {
    'datos_paciente': ['NO. CC:', 'NOMBRE:', 'EDAD:', 'EMPRESA:'],
    'ingresos': ['INGRESO', 'HOSPITALIZACIÓN', 'UCI'],
    'procedimientos': ['PROCEDIMIENTOS', 'NOTA DE ENFERMERÍA', 'EVOLUCIÓN'],
    'medicamentos': ['FÓRMULA MÉDICA', 'MEDICAMENTOS', 'ORDENES MÉDICAS'],
    'laboratorios': ['LABORATORIO', 'ORDENES DE LABORATORIO'],
    'imagenes': ['IMÁGENES', 'AYUDAS DIAGNÓSTICAS', 'RADIOLOGÍA']
}
