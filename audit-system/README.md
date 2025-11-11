# 🔍 Sistema de Auditoría Soberana

Sistema profesional de auditoría web con grabación de video en tiempo real, análisis con IA y cadena de custodia criptográfica para auditar sitios del Estado Mexicano.

## 🎯 Características Principales

### ✅ Auditoría Profesional Automatizada
- Extracción automatizada de datos estructurados
- Navegación inteligente con Playwright
- Detección automática de tablas, listas y contenido estructurado

### 🎥 Grabación de Video Forense
- Video en tiempo real de toda la sesión de auditoría (1920x1080)
- Screenshots sincronizados con timestamps
- Evidencia visual irrefutable de cada paso

### 🔐 Cadena de Custodia Criptográfica
- Sellado SHA-256 de todos los artefactos
- Manifiesto verificable con hashes
- Integridad garantizada de todas las evidencias

### 🤖 Análisis con IA (Gemini)
- Análisis inteligente de datos extraídos
- Detección automática de información sensible
- Generación de informes periciales profesionales

### 📊 Informes Completos
- **Resumen Ejecutivo**: Vista general de la auditoría
- **Informe de Análisis**: Análisis detallado con IA
- **Informe Pericial**: Documento forense profesional
- **Datos CSV**: Datos estructurados para análisis posterior

### 🏠 Soberanía Total
- Almacenamiento 100% local
- Sin dependencias de servicios externos
- Control total sobre los datos

## 🚀 Instalación

### Opción 1: Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/GABILANO/manus-agente.git
cd manus-agente/audit-system

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar navegadores de Playwright
playwright install chromium

# 5. Configurar API key de Gemini en ../.env
# Asegúrate de que existe GEMINI_API_KEY en el archivo .env
```

### Opción 2: Docker (Recomendado)

```bash
# 1. Construir imagen
docker build -t audit-system .

# 2. Ejecutar auditoría
docker run -v $(pwd)/audits:/app/audits \
  -e GEMINI_API_KEY=tu_api_key_aqui \
  audit-system https://ejemplo.gob.mx
```

## 📖 Uso

### Comando Básico

```bash
python main.py https://www2.scjn.gob.mx/ConsultasTematica/Resultados/-0-0-0-1-2025
```

### Comando Completo

```bash
python main.py \
  --prompt "Auditoría de expedientes SCJN 2025 para detectar datos sensibles" \
  --depth 4 \
  https://www2.scjn.gob.mx/ConsultasTematica/Resultados/-0-0-0-1-2025
```

### Parámetros

| Parámetro | Descripción | Requerido | Default |
|-----------|-------------|-----------|---------|
| `url` | URL del sitio a auditar | ✅ Sí | - |
| `-p, --prompt` | Objetivo de la auditoría | ❌ No | "Auditoría general" |
| `-d, --depth` | Profundidad (1-5) | ❌ No | 3 |

## 📁 Estructura de Salida

Cada auditoría genera un directorio con la siguiente estructura:

```
audits/audit_2025-11-11_14-30-45/
├── RESUMEN.md                  # Resumen ejecutivo
├── informe_analisis.md         # Análisis detallado con IA
├── informe_pericial.md         # Informe pericial forense
├── extracted_data.csv          # Datos extraídos
├── audit_session.webm          # Video de la sesión
├── audit.log                   # Log de eventos
├── manifest.json               # Manifiesto criptográfico
└── screenshots/                # Capturas de pantalla
    ├── 01_initial_load_143045.png
    ├── table_0_143046.png
    └── 99_extraction_complete_143050.png
```

## 🔍 Ejemplo de Auditoría: SCJN

### Comando

```bash
python main.py \
  --prompt "Auditar expedientes de la SCJN para identificar casos con datos sensibles y privación de libertad" \
  --depth 5 \
  "https://www2.scjn.gob.mx/ConsultasTematica/Resultados/-0-0-0-1-2025"
```

### Resultados Esperados

- ✅ Extracción de todos los expedientes visibles
- ✅ Identificación automática de casos marcados como "DATOS SENSIBLES"
- ✅ Detección de correlaciones con materia penal
- ✅ Video completo de la navegación y extracción
- ✅ Informe pericial con análisis de IA

## 🔐 Verificación de Integridad

Para verificar la integridad de una auditoría:

```bash
# 1. Ir al directorio de la auditoría
cd audits/audit_2025-11-11_14-30-45/

# 2. Verificar hash del manifiesto
sha256sum manifest.json

# 3. Verificar hashes de evidencias
sha256sum extracted_data.csv
sha256sum audit_session.webm

# 4. Comparar con los hashes en manifest.json
cat manifest.json | grep sha256
```

## 🏗️ Arquitectura del Sistema

### Agentes Especializados

El sistema implementa una arquitectura multi-agente orquestada con **LangGraph**:

```
┌─────────────────────────────────────────────────┐
│          Orquestador (LangGraph)                │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Evidence    │ │   Data   │ │   Crypto     │
│  Collector   │ │ Analyst  │ │  Forensics   │
│              │ │          │ │              │
│ • Playwright │ │ • Gemini │ │ • SHA-256    │
│ • Video Rec  │ │ • Pandas │ │ • Manifest   │
│ • Screenshots│ │ • Stats  │ │ • Chain      │
└──────────────┘ └──────────┘ └──────────────┘
```

### Flujo de Ejecución

1. **Inicialización**: Crear directorio, configurar log
2. **Recolección**: Navegar, extraer datos, grabar video
3. **Análisis**: Procesar datos con IA, detectar sensibles
4. **Sellado**: Calcular hashes, crear manifiesto
5. **Finalización**: Generar informes, resumen

## 📊 Casos de Uso

### 1. Auditoría de Transparencia Gubernamental

Auditar portales del Estado para verificar:
- Disponibilidad de información pública
- Clasificación correcta de datos sensibles
- Cumplimiento de normativa de transparencia

### 2. Análisis Forense de Sitios Web

Crear evidencia legal de:
- Estado de un sitio web en un momento específico
- Contenido publicado y su clasificación
- Cambios o inconsistencias

### 3. Monitoreo de Cumplimiento

Auditorías periódicas para:
- Detectar cambios en clasificación de información
- Identificar nuevos datos sensibles
- Generar series temporales de análisis

## 🛠️ Tecnologías Utilizadas

- **Python 3.11**: Lenguaje principal
- **Playwright**: Automatización de navegador con video
- **LangGraph**: Orquestación de agentes
- **Gemini 2.0 Flash**: Análisis con IA
- **Pandas**: Procesamiento de datos
- **BeautifulSoup**: Parsing HTML
- **Cryptography**: Sellado criptográfico

## 📝 Configuración Avanzada

### Variables de Entorno

Editar `../.env`:

```bash
# API de Gemini (requerida)
GEMINI_API_KEY=tu_api_key_aqui

# Configuración de auditoría
AUDIT_OUTPUT_DIR=/ruta/personalizada/audits
AUDIT_VIDEO_ENABLED=true
AUDIT_CRYPTO_ENABLED=true
```

### Personalización de Detección de Sensibles

Editar `agents/evidence_collector.py`, método `_detect_sensitive_keywords()`:

```python
sensitive_keywords = [
    'datos sensibles',
    'privado de libertad',
    # Añadir tus propias palabras clave
    'mi_palabra_clave',
]
```

## 🤝 Contribuir

Este sistema está diseñado para ser extensible. Áreas de mejora:

- [ ] Soporte para autenticación en sitios web
- [ ] Exportación de video a MP4 con ffmpeg
- [ ] Dashboard web interactivo con Gradio
- [ ] Integración con bases de datos externas
- [ ] Análisis de series temporales

## 📄 Licencia

Ver archivo LICENSE en el repositorio principal.

## 👤 Autor

**Sistema de Auditoría Soberana v1.0**
Desarrollado para auditorías profesionales del Estado Mexicano

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar los logs en `audits/[audit_id]/audit.log`
2. Verificar la configuración de GEMINI_API_KEY
3. Asegurar que Playwright está instalado: `playwright install chromium`

## 🎓 Fundamentos Teóricos

Este sistema se basa en:
- **Cadenas de Markov**: Modelado del proceso de auditoría
- **Procesos de Decisión de Markov (MDP)**: Orquestación de agentes
- **Conjetura de Collatz (3n+1)**: Filosofía de expansión/contracción
- **Cadena de Custodia Digital**: Estándares forenses internacionales

Para más detalles, ver documentos de análisis en el repositorio.
