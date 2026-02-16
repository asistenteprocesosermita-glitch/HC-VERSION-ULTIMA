# utils/extractor.py - Versión completa y funcional

import re
from typing import List, Dict, Any, Optional

# =============================================================================
# CONSTANTES (copiadas de config.py para que sea autónomo)
# =============================================================================

PATRON_FECHA = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
PATRON_FECHA_HORA = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?)\b'

PATRONES_PACIENTE = {
    'cc': r'No\.?\s*CC:\s*(\d+)',
    'nombre': r'Nombre:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\n|Edad|Fecha)',
    'edad': r'Edad actual:\s*(\d+)',
    'eps': r'Empresa:\s*(.+?)(?:\n|$)',
    'telefono': r'Tel(?:é|e)fono:\s*(\d+)',
    'responsable': r'Responsable:\s*(.+?)(?:\n|$)',
}

PROCEDIMIENTOS_KEYWORDS = [
    'biopsia', 'catéter venoso central', 'intubación', 'toracocentesis',
    'transfusión de glóbulos rojos', 'transfusión de plaquetas',
    'ventilación mecánica invasiva', 'ventilación mecánica no invasiva',
    'sonda vesical', 'sonda orogástrica', 'colocación de', 'curación de catéter',
    'ecografía pleural', 'marcaje', 'toma de muestras', 'quimioterapia'
]

MEDICAMENTOS_KEYWORDS = [
    'citarabina', 'idarrubicina', 'meropenem', 'vancomicina', 'piperacilina', 'tazobactam',
    'fluconazol', 'aciclovir', 'filgrastim', 'norepinefrina', 'fentanilo', 'midazolam',
    'amiodarona', 'ácido tranexámico', 'furosemida', 'omeprazol'
]

LABORATORIOS_KEYWORDS = [
    'hemograma', 'hematología', 'coagulación', 'tp', 'tpt', 'fibrinógeno',
    'creatinina', 'bun', 'nitrógeno ureico', 'glicemia', 'glucosa',
    'transaminasas', 'alt', 'ast', 'bilirrubinas', 'ldh', 'calcio', 'magnesio',
    'ionograma', 'sodio', 'potasio', 'cloro', 'gases arteriales', 'ácido láctico',
    'hemocultivo', 'urocultivo', 'coprocultivo', 'perfil lipídico',
    'hemoglobina', 'hematocrito', 'plaquetas', 'leucocitos', 'neutrófilos'
]

IMAGENES_KEYWORDS = [
    'radiografía', 'rayos x', 'ecografía', 'ultrasonido', 'tomografía', 'tac',
    'resonancia', 'rmn', 'mamografía', 'ecocardiograma', 'doppler'
]

INTERCONSULTAS_KEYWORDS = [
    'medicina interna', 'hematología', 'nutrición', 'psicología', 'cirugía general',
    'fisioterapia', 'neumología', 'cuidados intensivos'
]

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def normalizar_texto(texto: str) -> str:
    """Elimina espacios redundantes y saltos de línea."""
    return re.sub(r'\s+', ' ', texto).strip() if texto else ""

def extraer_fechas(texto: str, con_hora: bool = False) -> List[str]:
    """Extrae todas las fechas (con o sin hora) de un texto."""
    patron = PATRON_FECHA_HORA if con_hora else PATRON_FECHA
    return re.findall(patron, texto)

def segmentar_por_secciones(texto: str) -> Dict[str, str]:
    """
    Divide el texto en secciones basándose en palabras clave.
    Versión simplificada para no depender de config.py.
    """
    # Usamos las mismas secciones que en config.py
    secciones_lista = [
        'DATOS DEL PACIENTE', 'IDENTIFICACIÓN', 'INGRESO', 'EVOLUCIÓN',
        'NOTAS DE ENFERMERÍA', 'ORDENES MÉDICAS', 'FÓRMULA MÉDICA',
        'LABORATORIO', 'AYUDAS DIAGNÓSTICAS', 'INTERCONSULTAS',
        'PROCEDIMIENTOS', 'QUIMIOTERAPIA', 'TRANSFUSIONES', 'EPICRISIS'
    ]
    lineas = texto.split('\n')
    secciones = {}
    seccion_actual = "GENERAL"
    contenido_actual = []
    for linea in lineas:
        linea_upper = linea.upper()
        for sec in secciones_lista:
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
# FUNCIONES DE EXTRACCIÓN ESPECÍFICAS
# =============================================================================

def extraer_info_paciente(texto: str) -> Dict[str, Any]:
    info = {}
    for clave, patron in PATRONES_PACIENTE.items():
        match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            info[clave] = match.group(1).strip()
    return info

def extraer_estancias(texto: str) -> List[Dict[str, Any]]:
    eventos = []
    lineas = texto.split('\n')
    servicios_keywords = ['hospitalización', 'uci', 'cuidados intensivos']
    for i, linea in enumerate(lineas):
        linea_low = linea.lower()
        if any(s in linea_low for s in servicios_keywords):
            tipo = None
            if 'ingreso' in linea_low or 'traslado a' in linea_low:
                tipo = 'ingreso'
            elif 'egreso' in linea_low or 'traslado de' in linea_low:
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
    proc = []
    texto_busqueda = texto
    if secciones:
        texto_busqueda = secciones.get('PROCEDIMIENTOS', '') + '\n' + secciones.get('NOTAS DE ENFERMERÍA', '')
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in PROCEDIMIENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                proc.append({'procedimiento': linea.strip(), 'fecha': fecha})
                break
    return proc

def extraer_medicamentos(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    meds = []
    texto_busqueda = texto
    if secciones:
        texto_busqueda = secciones.get('FÓRMULA MÉDICA', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in MEDICAMENTOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                meds.append({'medicamento': linea.strip(), 'fecha': fecha})
                break
    return meds

def extraer_laboratorios(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    labs = []
    texto_busqueda = texto
    if secciones:
        texto_busqueda = secciones.get('LABORATORIO', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in LABORATORIOS_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                labs.append({'examen': linea.strip(), 'fecha': fecha})
                break
    return labs

def extraer_imagenes(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    imgs = []
    texto_busqueda = texto
    if secciones:
        texto_busqueda = secciones.get('AYUDAS DIAGNÓSTICAS', '') + '\n' + secciones.get('ORDENES MÉDICAS', '')
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        for kw in IMAGENES_KEYWORDS:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                imgs.append({'estudio': linea.strip(), 'fecha': fecha})
                break
    return imgs

def extraer_interconsultas(texto: str, secciones: Dict[str, str] = None) -> List[Dict[str, Any]]:
    inter = []
    texto_busqueda = texto
    if secciones:
        texto_busqueda = secciones.get('INTERCONSULTAS', '') + '\n' + secciones.get('EVOLUCIÓN', '')
    lineas = texto_busqueda.split('\n')
    for linea in lineas:
        if 'interconsulta' in linea.lower() or 'valoración por' in linea.lower():
            for kw in INTERCONSULTAS_KEYWORDS:
                if kw.lower() in linea.lower():
                    fechas = extraer_fechas(linea, con_hora=True)
                    fecha = fechas[0] if fechas else None
                    inter.append({'especialidad': kw.capitalize(), 'descripcion': linea.strip(), 'fecha': fecha})
                    break
    return inter

def extraer_transfusiones(texto: str) -> List[Dict[str, Any]]:
    trans = []
    patron = r'(transfusión|administración)\s+(?:de\s+)?(\d+\s*(?:unidades?|pool|plaquetas?|glóbulos?|GRE?|GR))'
    lineas = texto.split('\n')
    for linea in lineas:
        match = re.search(patron, linea, re.IGNORECASE)
        if match:
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            trans.append({'descripcion': linea.strip(), 'fecha': fecha})
    return trans

def extraer_soporte_ventilatorio(texto: str) -> List[Dict[str, Any]]:
    soporte = []
    lineas = texto.split('\n')
    for linea in lineas:
        if re.search(r'ventilaci[oó]n mec[aá]nica invasiva|vmi|intubado', linea, re.IGNORECASE):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            soporte.append({'tipo': 'VMI', 'fecha': fecha, 'descripcion': linea.strip()})
        elif re.search(r'ventilaci[oó]n mec[aá]nica no invasiva|vmni|cpap|bipap', linea, re.IGNORECASE):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            soporte.append({'tipo': 'VMNI', 'fecha': fecha, 'descripcion': linea.strip()})
    return soporte

def extraer_notas_enfermeria_relevantes(texto: str) -> List[Dict[str, Any]]:
    notas = []
    keywords = ['canalización', 'venopunción', 'toma de muestras', 'curación', 'administración de', 'transfusión']
    lineas = texto.split('\n')
    for linea in lineas:
        for kw in keywords:
            if kw.lower() in linea.lower():
                fechas = extraer_fechas(linea, con_hora=True)
                fecha = fechas[0] if fechas else None
                notas.append({'nota': linea.strip(), 'fecha': fecha})
                break
    return notas

def extraer_ordenamientos_laboratorio(texto: str) -> List[Dict[str, Any]]:
    ordenes = []
    lineas = texto.split('\n')
    for linea in lineas:
        if 'orden' in linea.lower() and any(kw in linea.lower() for kw in LABORATORIOS_KEYWORDS[:5]):
            fechas = extraer_fechas(linea, con_hora=True)
            fecha = fechas[0] if fechas else None
            ordenes.append({'orden': linea.strip(), 'fecha': fecha})
    return ordenes

def extraer_evoluciones_clave(texto: str) -> List[Dict[str, Any]]:
    evol = []
    lineas = texto.split('\n')
    en_evolucion = False
    bloque = []
    for linea in lineas:
        if 'evoluci' in linea.lower() and ('médica' in linea.lower() or 'medico' in linea.lower()):
            en_evolucion = True
            if bloque:
                evol.append('\n'.join(bloque))
                bloque = []
        if en_evolucion:
            bloque.append(linea)
            if len(bloque) > 10:
                evol.append('\n'.join(bloque))
                bloque = []
                en_evolucion = False
    if bloque:
        evol.append('\n'.join(bloque))
    resultado = []
    for ev in evol:
        fechas = extraer_fechas(ev, con_hora=True)
        fecha = fechas[0] if fechas else None
        resultado.append({'evolucion': ev[:200] + '...', 'fecha': fecha})
    return resultado

# =============================================================================
# FUNCIÓN PRINCIPAL (exportada)
# =============================================================================

def extraer_todo(texto: str) -> Dict[str, Any]:
    texto_norm = normalizar_texto(texto)
    secciones = segmentar_por_secciones(texto_norm)
    return {
        'paciente': extraer_info_paciente(texto_norm),
        'estancias': extraer_estancias(texto_norm),
        'procedimientos': extraer_procedimientos(texto_norm, secciones),
        'medicamentos': extraer_medicamentos(texto_norm, secciones),
        'laboratorios': extraer_laboratorios(texto_norm, secciones),
        'imagenes': extraer_imagenes(texto_norm, secciones),
        'interconsultas': extraer_interconsultas(texto_norm, secciones),
        'transfusiones': extraer_transfusiones(texto_norm),
        'soporte_ventilatorio': extraer_soporte_ventilatorio(texto_norm),
        'notas_enfermeria': extraer_notas_enfermeria_relevantes(texto_norm),
        'ordenamientos_lab': extraer_ordenamientos_laboratorio(texto_norm),
        'evoluciones_clave': extraer_evoluciones_clave(texto_norm)
    }
