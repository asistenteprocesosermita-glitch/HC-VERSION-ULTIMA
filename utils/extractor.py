"""
Módulo de extracción de información facturable de historias clínicas.
Versión estable y libre de errores de importación.
"""

import re
import logging
from typing import List, Dict, Any, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTES Y PATRONES
# =============================================================================

PATRON_FECHA = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
PATRON_FECHA_HORA = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?)\b'

PATRONES_PACIENTE = {
    'cc': r'No\.?\s*C[CG]\s*:?\s*(\d+)',
    'nombre': r'Nombre\s*:?\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Edad|Fecha|Nacimiento)',
    'edad': r'Edad\s*(?:actual)?\s*:?\s*(\d+)\s*(?:años?)',
    'fecha_nacimiento': r'Fecha\s*(?:de\s*)?[Nn]acimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    'eps': r'Empresa\s*:?\s*(.+?)(?:\n|$)',
    'telefono': r'Tel[ée]fono\s*:?\s*(\d+)',
    'responsable': r'Responsable\s*:?\s*(.+?)(?:\n|$)',
    'regimen': r'R[ée]gimen\s*:?\s*(Contributivo|Subsidiado|Vinculado)',
    'afiliado': r'Afiliado\s*:?\s*(Cotizante|Beneficiario)'
}

PROCEDIMIENTOS_KEYWORDS = [
    'biopsia de médula ósea', 'biopsia', 'aspirado de médula ósea', 'mielograma',
    'catéter venoso central', 'cvc', 'colocación de catéter', 'catéter subclavio',
    'intubación orotraqueal', 'intubación', 'toracocentesis', 'paracentesis',
    'transfusión de glóbulos rojos', 'transfusión de plaquetas', 'transfusión sanguínea',
    'ventilación mecánica invasiva', 'vmi', 'ventilación mecánica no invasiva', 'vmni',
    'sonda vesical', 'sonda orogástrica', 'sonda nasogástrica', 'colocación de sonda',
    'curación de catéter', 'curación', 'ecografía pleural', 'marcaje ecográfico',
    'toma de muestras', 'quimioterapia', 'infusión de quimioterapia',
    'ecocardiograma', 'hemocultivo', 'urocultivo', 'cultivo', 'drenaje'
]

MEDICAMENTOS_KEYWORDS = [
    'citarabina', 'ara-c', 'idarrubicina', 'idarubicina', 'daunorrubicina',
    'meropenem', 'vancomicina', 'piperacilina', 'tazobactam', 'imepenem',
    'cefepime', 'ceftriaxona', 'ampicilina', 'sulbactam',
    'fluconazol', 'anfotericina', 'caspofungina',
    'aciclovir', 'valaciclovir', 'ganciclovir',
    'filgrastim', 'pegfilgrastim', 'eritropoyetina',
    'norepinefrina', 'noradrenalina', 'dopamina', 'dobutamina', 'vasopresina',
    'fentanilo', 'midazolam', 'propofol', 'ketamina', 'morfina',
    'amiodarona', 'lidocaína',
    'ácido tranexámico', 'furosemida', 'omeprazol', 'levotiroxina', 'acetaminofén',
    'amitriptilina', 'trimebutina', 'bisacodilo', 'ondansetrón', 'metoclopramida',
    'trimetoprim', 'sulfametoxazol', 'lactulosa', 'loperamida', 'insulina glargina',
    'cloruro de potasio', 'kcl', 'gluconato de calcio', 'sulfato de magnesio'
]

LABORATORIOS_KEYWORDS = [
    'hemograma', 'hematología', 'serie roja', 'serie blanca', 'plaquetas',
    'coagulación', 'tp', 'tpt', 'inr', 'fibrinógeno', 'creatinina', 'bun',
    'nitrógeno ureico', 'glicemia', 'glucosa', 'transaminasas', 'alt', 'ast',
    'bilirrubinas', 'ldh', 'calcio', 'magnesio', 'fósforo', 'ionograma', 'sodio',
    'potasio', 'cloro', 'gases arteriales', 'gasometría', 'ácido láctico', 'lactato',
    'hemocultivo', 'urocultivo', 'coprocultivo', 'perfil lipídico', 'colesterol',
    'triglicéridos', 'hemoglobina', 'hematocrito', 'leucocitos', 'neutrófilos',
    'linfocitos', 'ferritina', 'transferrina', 'haptoglobina', 'coombs',
    'anticardiolipinas', 'antifosfolípidos', 'anticoagulante lúpico', 'ana',
    'ácido fólico', 'vitamina b12', 'parcial de orina', 'uroanálisis'
]

IMAGENES_KEYWORDS = [
    'radiografía', 'rayos x', 'ecografía', 'ultrasonido', 'tomografía', 'tac',
    'resonancia', 'rmn', 'mamografía', 'ecocardiograma', 'doppler', 'seriada',
    'angiografía', 'fluoroscopia', 'pet', 'spect'
]

INTERCONSULTAS_KEYWORDS = [
    'medicina interna', 'hematología', 'oncología', 'nutrición', 'dietética',
    'psicología', 'psiquiatría', 'cirugía general', 'cirugía cardiovascular',
    'fisioterapia', 'terapia respiratoria', 'neumología', 'cuidados intensivos',
    'infectología', 'nefrología', 'gastroenterología', 'cardiología'
]

SECCIONES = [
    'DATOS DEL PACIENTE', 'IDENTIFICACIÓN', 'INGRESO', 'EVOLUCIÓN',
    'NOTAS DE ENFERMERÍA', 'ORDENES MÉDICAS', 'FÓRMULA MÉDICA',
    'LABORATORIO', 'AYUDAS DIAGNÓSTICAS', 'INTERCONSULTAS',
    'PROCEDIMIENTOS', 'QUIMIOTERAPIA', 'TRANSFUSIONES', 'EPICRISIS'
]

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def normalizar_texto(texto: str) -> str:
    """Elimina espacios redundantes y saltos de línea."""
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', texto).strip()

def extraer_fechas(texto: str, con_hora: bool = False) -> List[str]:
    """Extrae todas las fechas (con o sin hora) de un texto."""
    patron = PATRON_FECHA_HORA if con_hora else PATRON_FECHA
    return re.findall(patron, texto)

def parsear_dosis_via(texto: str) -> Dict[str, str]:
    """Extrae dosis, vía y frecuencia de una línea de medicamento."""
    resultado = {}
    patron_dosis = r'(\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|UI|ml))'
    dosis_match = re.search(patron_dosis, texto, re.IGNORECASE)
    if dosis_match:
        resultado['dosis'] = dosis_match.group(1)
    patron_via = r'\b(IV|VO|SC|IM|EV|intravenosa|oral|subcutánea|intramuscular)\b'
    via_match = re.search(patron_via, texto, re.IGNORECASE)
    if via_match:
        resultado['via'] = via_match.group(1).upper()
    patron_frec = r'(cada\s+\d+\s*(?:h|horas?)|(?:una|dos|tres)?\s*veces\s*al\s*d[íi]a|QD|BID|TID|QID|c\/\d+\s*h)'
    frec_match = re.search(patron_frec, texto, re.IGNORECASE)
    if frec_match:
        resultado['frecuencia'] = frec_match.group(1).lower()
    return resultado

def segmentar_por_secciones(texto: str) -> Dict[str, str]:
    """Divide el texto en secciones basándose en palabras clave."""
    lineas = texto.split('\n')
    secciones = {}
    seccion_actual = "GENERAL"
    contenido_actual = []
    for linea in lineas:
        linea_upper = linea.upper()
        for sec in SECCIONES:
            if sec in linea_upper:
                if contenido_actual:
                    secciones[seccion_actual] = '\n'.join(contenido_actual).strip()
                seccion_actual = sec
                contenido_actual = []
                break
        else:
            contenido_actual.append(linea)
    if contenido_actual:
        secciones[seccion_actual] = '\n'.join(contenido_actual).strip()
    return secciones

# =============================================================================
# FUNCIONES DE EXTRACCIÓN
# =============================================================================

def extraer_info_paciente(texto: str) -> Dict[str, Any]:
    """Extrae datos del paciente usando patrones."""
    info = {}
    for clave, patron in PATRONES_PACIENTE.items():
        match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            valor = match.group(1).strip()
            valor = re.sub(r'\s+', ' ', valor)
            info[clave] = valor
    return info

def extraer_estancias(texto: str) -> List[Dict[str, Any]]:
    """Detecta eventos de ingreso, traslado y egreso por servicio."""
    eventos = []
    lineas = texto.split('\n')
    servicios_keywords = ['hospitalización', 'uci', 'cuidados intensivos', 
                         'hospitalización general', '5 piso', '4 piso', 'urgencias']
    for i, linea in enumerate(lineas):
        linea_low = linea.lower()
        if any(s in linea_low for s in servicios_keywords):
            tipo = None
            if 'ingreso' in linea_low or 'traslado a' in linea_low or 'admisión' in linea_low:
                tipo = 'ingreso'
            elif 'egreso' in linea_low or 'traslado de' in linea_low or 'salida' in linea_low:
                tipo = 'egreso'
            if not tipo:
                continue
            fechas = extraer_fechas(linea, con_hora=True)
            if not fechas and i+1 < len(lineas):
                fechas = extraer_fechas(lineas[i+1], con_hora=True)
            if fechas:
                fecha_hora = fechas[0]
                if ' ' in fecha_hora:
                    fecha, hora = fecha_hora.split(' ', 1)
                else:
                    fecha, hora = fecha_hora, ''
                eventos.append({
                    'servicio': linea.strip(),
                    'fecha': fecha,
                    'hora': hora,
                    'tipo': tipo
                })
    eventos.sort(key=lambda x: x['fecha'])
    return eventos

def extraer_procedimientos(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Busca procedimientos en todo el texto o en secciones específicas."""
    procedimientos = []
    if secciones:
        texto_busqueda = secciones.get('PROCEDIMIENTOS', '') + '\n' + secciones.get('NOTAS DE ENFERMERÍA', '')
    else:
        texto_busqueda = texto
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in PROCEDIMIENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                es_mayor = any(x in kw for x in ['biopsia', 'catéter', 'intubación', 'toracocentesis', 'ventilación'])
                procedimientos.append({
                    'procedimiento': linea.strip(),
                    'fecha': fecha,
                    'categoria': 'mayor' if es_mayor else 'menor',
                    'keyword_detectada': kw
                })
                break
    return procedimientos

def extraer_medicamentos(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Extrae medicamentos, preferentemente de secciones de fórmula médica."""
    medicamentos = []
    if secciones:
        texto_busqueda = secciones.get('FÓRMULA MÉDICA', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    else:
        texto_busqueda = texto
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in MEDICAMENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                dosis_via = parsear_dosis_via(linea)
                medicamentos.append({
                    'medicamento': linea.strip(),
                    'fecha': fecha,
                    **dosis_via
                })
                break
    return medicamentos

def extraer_laboratorios(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Extrae exámenes de laboratorio ordenados o resultados."""
    laboratorios = []
    if secciones:
        texto_busqueda = secciones.get('LABORATORIO', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    else:
        texto_busqueda = texto
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in LABORATORIOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                laboratorios.append({
                    'examen': linea.strip(),
                    'fecha': fecha,
                    'tipo': 'laboratorio'
                })
                break
    return laboratorios

def extraer_imagenes(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Extrae estudios de imágenes diagnósticas."""
    imagenes = []
    if secciones:
        texto_busqueda = secciones.get('AYUDAS DIAGNÓSTICAS', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    else:
        texto_busqueda = texto
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in IMAGENES_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                imagenes.append({
                    'estudio': linea.strip(),
                    'fecha': fecha,
                    'modalidad': kw.capitalize()
                })
                break
    return imagenes

def extraer_interconsultas(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Extrae interconsultas o valoraciones por especialistas."""
    interconsultas = []
    if secciones:
        texto_busqueda = secciones.get('INTERCONSULTAS', '') + '\n' + secciones.get('EVOLUCIÓN', '')
    else:
        texto_busqueda = texto
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        if 'interconsulta' in linea.lower() or 'valoración por' in linea.lower():
            for kw in INTERCONSULTAS_KEYWORDS:
                if kw.lower() in linea.lower():
                    fechas = extraer_fechas(linea, con_hora=True)
                    fecha = fechas[0] if fechas else None
                    interconsultas.append({
                        'especialidad': kw.capitalize(),
                        'descripcion': linea.strip(),
                        'fecha': fecha
                    })
                    break
    return interconsultas

def extraer_transfusiones(texto: str) -> List[Dict[str, Any]]:
    """Busca específicamente transfusiones de hemoderivados."""
    transfusiones = []
    patron_transfusion = r'(transfusión|administración)\s+(?:de\s+)?(\d+\s*(?:unidades?|pool|plaquetas?|glóbulos?|GRE?|GR))'
    lineas = texto.split('\n')
    for linea in lineas:
        match = re.search(patron_transfusion, linea, re.IGNORECASE)
        if match:
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            transfusiones.append({
                'descripcion': linea.strip(),
                'fecha': fecha,
                'tipo': match.group(2)
            })
    return transfusiones

def extraer_soporte_ventilatorio(texto: str) -> List[Dict[str, Any]]:
    """Identifica días de ventilación mecánica (invasiva/no invasiva)."""
    soporte = []
    patron_vmi = r'ventilaci[oó]n mec[aá]nica invasiva|vmi|intubado'
    patron_vmni = r'ventilaci[oó]n mec[aá]nica no invasiva|vmni|cpap|bipap'
    lineas = texto.split('\n')
    for linea in lineas:
        if re.search(patron_vmi, linea, re.IGNORECASE):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            soporte.append({'tipo': 'VMI', 'fecha': fecha, 'descripcion': linea.strip()})
        elif re.search(patron_vmni, linea, re.IGNORECASE):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            soporte.append({'tipo': 'VMNI', 'fecha': fecha, 'descripcion': linea.strip()})
    return soporte

def extraer_notas_enfermeria_relevantes(texto: str) -> List[Dict[str, Any]]:
    """Extrae notas de enfermería que mencionan procedimientos o cuidados facturables."""
    notas = []
    keywords_enfermeria = [
        'canalización', 'venopunción', 'toma de muestras', 'curación',
        'administración de', 'transfusión', 'control de signos', 'balance',
        'escala de braden', 'riesgo de caídas', 'sonda', 'catéter'
    ]
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in keywords_enfermeria:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                notas.append({
                    'nota': linea.strip(),
                    'fecha': fecha,
                    'keyword': kw
                })
                break
    return notas

def extraer_ordenamientos_laboratorio(texto: str) -> List[Dict[str, Any]]:
    """Identifica órdenes específicas de laboratorio."""
    ordenes = []
    lineas = texto.split('\n')
    for linea in lineas:
        if 'orden' in linea.lower() and any(kw in linea.lower() for kw in LABORATORIOS_KEYWORDS[:10]):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            ordenes.append({
                'orden': linea.strip(),
                'fecha': fecha
            })
    return ordenes

def extraer_evoluciones_clave(texto: str) -> List[Dict[str, Any]]:
    """Extrae fragmentos de evoluciones médicas que justifiquen procedimientos o estancia."""
    evoluciones = []
    lineas = texto.split('\n')
    en_evolucion = False
    bloque = []
    for linea in lineas:
        if 'evoluci' in linea.lower() and ('médica' in linea.lower() or 'medico' in linea.lower()):
            en_evolucion = True
            if bloque:
                evoluciones.append('\n'.join(bloque))
                bloque = []
        if en_evolucion:
            bloque.append(linea)
            if len(bloque) > 10:
                evoluciones.append('\n'.join(bloque))
                bloque = []
                en_evolucion = False
    if bloque:
        evoluciones.append('\n'.join(bloque))
    resultado = []
    for ev in evoluciones:
        fechas = extraer_fechas(ev, con_hora=True)
        fecha = fechas[0] if fechas else None
        resultado.append({'evolucion': ev[:200] + '...', 'fecha': fecha})
    return resultado

# =============================================================================
# FUNCIÓN PRINCIPAL (LA QUE IMPORTA APP.PY)
# =============================================================================

def extraer_todo(texto: str) -> Dict[str, Any]:
    """
    Ejecuta todas las extracciones y retorna un diccionario completo.
    Esta es la función que importamos en app.py.
    """
    texto_normalizado = normalizar_texto(texto)
    secciones = segmentar_por_secciones(texto_normalizado)
    
    resultado = {
        'paciente': extraer_info_paciente(texto_normalizado),
        'estancias': extraer_estancias(texto_normalizado),
        'procedimientos': extraer_procedimientos(texto_normalizado, secciones),
        'medicamentos': extraer_medicamentos(texto_normalizado, secciones),
        'laboratorios': extraer_laboratorios(texto_normalizado, secciones),
        'imagenes': extraer_imagenes(texto_normalizado, secciones),
        'interconsultas': extraer_interconsultas(texto_normalizado, secciones),
        'transfusiones': extraer_transfusiones(texto_normalizado),
        'soporte_ventilatorio': extraer_soporte_ventilatorio(texto_normalizado),
        'notas_enfermeria': extraer_notas_enfermeria_relevantes(texto_normalizado),
        'ordenamientos_lab': extraer_ordenamientos_laboratorio(texto_normalizado),
        'evoluciones_clave': extraer_evoluciones_clave(texto_normalizado)
    }
    return resultado

# =============================================================================
# BLOQUE DE PRUEBA (OPCIONAL)
# =============================================================================

if __name__ == "__main__":
    # Prueba rápida para verificar que todo funciona
    texto_prueba = """
    No. CC: 73129351
    Nombre: JAVIER ENRIQUE MARRUGO RODRIGUEZ
    Edad actual: 59 años
    Empresa: SALUD TOTAL EPSS S.A.
    
    INGRESO A HOSPITALIZACIÓN GENERAL: 30/10/2025 05:38
    Se realiza biopsia de médula ósea el 05/11/2025.
    Transfusión de 2 unidades de GRE el 07/11/2025.
    FÓRMULA MÉDICA: Citarabina 172 mg IV cada 24h.
    LABORATORIO: Hemograma 30/10/2025, creatinina 31/10/2025.
    INTERCONSULTA A HEMATOLOGÍA el 03/11/2025.
    """
    extraido = extraer_todo(texto_prueba)
    for k, v in extraido.items():
        print(f"\n{k.upper()}:")
        print(v)
