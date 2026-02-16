# Palabras clave para identificar secciones del documento
SECCIONES = {
    'datos_paciente': ['NO. CC:', 'NOMBRE:', 'EDAD:', 'EMPRESA:', 'AFILIADO'],
    'ingresos': ['INGRESO', 'HOSPITALIZACIÓN', 'UCI', 'CUIDADOS INTENSIVOS'],
    'procedimientos': ['PROCEDIMIENTOS', 'NOTA DE ENFERMERÍA', 'EVOLUCIÓN', 'REPORTE QUIRÚRGICO'],
    'medicamentos': ['FÓRMULA MÉDICA', 'MEDICAMENTOS', 'ORDENES MÉDICAS', 'TRATAMIENTO'],
    'laboratorios': ['LABORATORIO', 'ORDENES DE LABORATORIO', 'EXÁMENES DE LABORATORIO'],
    'imagenes': ['IMÁGENES', 'AYUDAS DIAGNÓSTICAS', 'RADIOLOGÍA', 'ECOGRAFÍA', 'TOMOGRAFÍA'],
    'interconsultas': ['INTERCONSULTA', 'VALORACIÓN POR', ' remisión a '],
}

# Patrones para extraer datos del paciente
PATRONES_PACIENTE = {
    'cc': r'No\.?\s*CC:\s*(\d+)',
    'nombre': r'Nombre:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Edad|Fecha)',
    'edad': r'Edad actual:\s*(\d+)',
    'eps': r'Empresa:\s*(.+?)(?:\n|$)',
    'telefono': r'Tel(?:é|e)fono:\s*(\d+)',
    'responsable': r'Responsable:\s*(.+?)(?:\n|$)',
}

# Palabras clave para procedimientos
PROCEDIMIENTOS_KEYWORDS = [
    'biopsia', 'catéter venoso central', 'intubación', 'toracocentesis',
    'transfusión de glóbulos rojos', 'transfusión de plaquetas',
    'ventilación mecánica invasiva', 'ventilación mecánica no invasiva',
    'sonda vesical', 'sonda orogástrica', 'colocación de', 'curación de catéter',
    'ecografía pleural', 'marcaje', 'toma de muestras', 'quimioterapia'
]

# Palabras clave para medicamentos (de alto costo o relevantes)
MEDICAMENTOS_KEYWORDS = [
    'citarabina', 'idarrubicina', 'meropenem', 'vancomicina', 'piperacilina', 'tazobactam',
    'fluconazol', 'aciclovir', 'filgrastim', 'norepinefrina', 'fentanilo', 'midazolam',
    'amiodarona', 'ácido tranexámico', 'furosemida', 'omeprazol'
]

# Palabras clave para laboratorios
LABORATORIOS_KEYWORDS = [
    'hemograma', 'hematología', 'coagulación', 'tp', 'tpt', 'fibrinógeno',
    'creatinina', 'bun', 'nitrógeno ureico', 'glicemia', 'glucosa',
    'transaminasas', 'alt', 'ast', 'bilirrubinas', 'ldh', 'calcio', 'magnesio',
    'ionograma', 'sodio', 'potasio', 'cloro', 'gases arteriales', 'ácido láctico',
    'hemocultivo', 'urocultivo', 'coprocultivo', 'perfil lipídico',
    'hemoglobina', 'hematocrito', 'plaquetas', 'leucocitos', 'neutrófilos'
]

# Palabras clave para imágenes diagnósticas
IMAGENES_KEYWORDS = [
    'radiografía', 'rayos x', 'ecografía', 'ultrasonido', 'tomografía', 'tac',
    'resonancia', 'rmn', 'mamografía', 'ecocardiograma', 'doppler'
]

# Palabras clave para interconsultas
INTERCONSULTAS_KEYWORDS = [
    'medicina interna', 'hematología', 'nutrición', 'psicología', 'cirugía general',
    'fisioterapia', 'neumología', 'cuidados intensivos'
]

# Patrón genérico para fechas (dd/mm/aaaa o dd-mm-aaaa)
PATRON_FECHA = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
