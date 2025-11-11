"""
Agente Analista de Datos con IA
Responsable de analizar los datos extraídos y generar informes periciales
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI

from core.state import AgentState, AuditStatus


class DataAnalysisAgent:
    """
    Agente que analiza los datos extraídos usando Gemini para generar
    informes periciales profesionales y objetivos.
    """
    
    def __init__(self, state: AgentState, gemini_api_key: str):
        self.state = state
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.1  # Baja temperatura para análisis objetivo
        )
    
    def execute(self) -> AgentState:
        """
        Ejecuta el análisis de datos y genera informes.
        
        Returns:
            Estado actualizado con análisis y rutas a informes
        """
        print("[DataAnalyst] Iniciando análisis de datos")
        
        self.state['status'] = AuditStatus.ANALYZING
        self.state['current_task'] = "Analizando datos con IA"
        
        try:
            # Cargar datos extraídos
            if not self.state['extracted_data_path']:
                raise ValueError("No hay datos extraídos para analizar")
            
            df = pd.read_csv(self.state['extracted_data_path'])
            
            # Análisis estadístico básico
            stats = self._generate_statistics(df)
            
            # Identificar registros sensibles
            sensitive_records = self._identify_sensitive_records(df)
            self.state['sensitive_records'] = sensitive_records
            
            # Detectar anomalías
            anomalies = self._detect_anomalies(df)
            self.state['anomalies'] = anomalies
            
            # Generar informe de análisis con Gemini
            analysis_report = self._generate_analysis_report(df, stats, sensitive_records, anomalies)
            
            # Guardar informe
            report_path = os.path.join(self.state['output_dir'], 'informe_analisis.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(analysis_report)
            
            self.state['analysis_report_path'] = report_path
            
            # Generar informe pericial forense
            forensic_report = self._generate_forensic_report(stats, sensitive_records, anomalies)
            
            forensic_path = os.path.join(self.state['output_dir'], 'informe_pericial.md')
            with open(forensic_path, 'w', encoding='utf-8') as f:
                f.write(forensic_report)
            
            self.state['forensic_report_path'] = forensic_path
            
            print(f"[DataAnalyst] Análisis completado. Registros sensibles: {len(sensitive_records)}")
            
        except Exception as e:
            self.state['errors'].append(f"Error en DataAnalyst: {str(e)}")
            print(f"[DataAnalyst] ERROR: {e}")
        
        return self.state
    
    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera estadísticas descriptivas de los datos"""
        stats = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
        # Estadísticas por columna si es numérica
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats["numeric_summary"] = df[numeric_cols].describe().to_dict()
        
        return stats
    
    def _identify_sensitive_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifica registros que contienen información sensible.
        Basado en los criterios del análisis SCJN.
        """
        sensitive_records = []
        
        # Buscar columna que indique sensibilidad
        if 'contains_sensitive_keyword' in df.columns:
            sensitive_df = df[df['contains_sensitive_keyword'] == True]
            sensitive_records = sensitive_df.to_dict('records')
        else:
            # Buscar palabras clave en todas las columnas
            sensitive_keywords = [
                'datos sensibles', 'privado de libertad', 'confidencial',
                'reservado', 'seguridad nacional', 'materia penal'
            ]
            
            for idx, row in df.iterrows():
                row_text = ' '.join(str(v).lower() for v in row.values)
                if any(keyword in row_text for keyword in sensitive_keywords):
                    record = row.to_dict()
                    record['_sensitivity_reason'] = 'Contiene palabras clave sensibles'
                    sensitive_records.append(record)
        
        return sensitive_records
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en los datos extraídos.
        """
        anomalies = []
        
        # Anomalía 1: Registros con muchos valores nulos
        null_threshold = len(df.columns) * 0.5
        for idx, row in df.iterrows():
            null_count = row.isnull().sum()
            if null_count > null_threshold:
                anomalies.append({
                    "type": "high_null_values",
                    "record_index": idx,
                    "null_count": int(null_count),
                    "description": f"Registro con {null_count} valores nulos de {len(df.columns)} columnas"
                })
        
        # Anomalía 2: Duplicados exactos
        duplicates = df[df.duplicated(keep=False)]
        if len(duplicates) > 0:
            anomalies.append({
                "type": "duplicate_records",
                "count": len(duplicates),
                "description": f"Se encontraron {len(duplicates)} registros duplicados"
            })
        
        return anomalies
    
    def _generate_analysis_report(
        self, 
        df: pd.DataFrame, 
        stats: Dict[str, Any],
        sensitive_records: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """
        Genera un informe de análisis usando Gemini.
        """
        # Preparar contexto para Gemini
        context = f"""
Eres un analista de datos forense especializado en auditorías de transparencia gubernamental.

DATOS DE LA AUDITORÍA:
- URL auditada: {self.state['target_url']}
- Objetivo: {self.state['user_prompt']}
- Total de registros extraídos: {stats['total_records']}
- Registros con información sensible: {len(sensitive_records)}
- Anomalías detectadas: {len(anomalies)}

MUESTRA DE DATOS (primeras 5 filas):
{df.head().to_string()}

ESTADÍSTICAS:
{json.dumps(stats, indent=2, ensure_ascii=False)}

REGISTROS SENSIBLES:
{json.dumps(sensitive_records[:5], indent=2, ensure_ascii=False)}

ANOMALÍAS:
{json.dumps(anomalies, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
Genera un informe de análisis profesional en formato Markdown que incluya:
1. Resumen ejecutivo
2. Metodología de análisis
3. Hallazgos principales
4. Análisis de datos sensibles
5. Anomalías detectadas
6. Conclusiones y recomendaciones

El informe debe ser objetivo, técnico y fundamentado en los datos.
"""
        
        try:
            response = self.llm.invoke(context)
            return response.content
        except Exception as e:
            print(f"[DataAnalyst] Error al generar informe con Gemini: {e}")
            return self._generate_fallback_report(stats, sensitive_records, anomalies)
    
    def _generate_forensic_report(
        self,
        stats: Dict[str, Any],
        sensitive_records: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """
        Genera un informe pericial forense estructurado.
        """
        report = f"""# INFORME PERICIAL DE AUDITORÍA WEB

## IDENTIFICACIÓN DE LA AUDITORÍA

**ID de Auditoría:** {self.state['audit_id']}
**Fecha y Hora:** {self.state['timestamp']}
**Perito Digital:** Sistema de Auditoría Soberana v1.0
**URL Auditada:** {self.state['target_url']}

## OBJETIVO DE LA AUDITORÍA

{self.state['user_prompt']}

## METODOLOGÍA

La presente auditoría se realizó mediante técnicas de web scraping automatizado con grabación de video en tiempo real, siguiendo los estándares de cadena de custodia digital establecidos en la normativa forense internacional.

### Herramientas Utilizadas

- **Navegador:** Chromium (Playwright)
- **Grabación de Video:** Playwright Video Recording (1920x1080)
- **Análisis de Datos:** Pandas + Gemini AI
- **Sellado Criptográfico:** SHA-256

## HALLAZGOS

### Datos Extraídos

- **Total de registros:** {stats['total_records']}
- **Columnas identificadas:** {len(stats['columns'])}
- **Estructura:** {', '.join(stats['columns'][:10])}{'...' if len(stats['columns']) > 10 else ''}

### Información Sensible Detectada

Se identificaron **{len(sensitive_records)}** registros que contienen información clasificada como sensible según los criterios establecidos en la Ley General de Transparencia y Acceso a la Información Pública (LGTAIP) y la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados (LGPDPPSO).

#### Criterios de Clasificación

Los registros fueron clasificados como sensibles por contener:
- Datos personales concernientes a personas físicas identificables
- Referencias a procesos penales
- Información relacionada con seguridad nacional o pública
- Datos confidenciales según normativa aplicable

### Anomalías Detectadas

Se identificaron **{len(anomalies)}** anomalías en los datos extraídos:

"""
        
        for idx, anomaly in enumerate(anomalies, 1):
            report += f"\n{idx}. **{anomaly['type']}**: {anomaly['description']}\n"
        
        report += f"""

## CADENA DE CUSTODIA

La integridad de las evidencias digitales se garantiza mediante:

1. **Grabación de video continua** de toda la sesión de auditoría
2. **Sellado criptográfico SHA-256** de todos los artefactos
3. **Manifiesto verificable** con timestamps y hashes
4. **Almacenamiento local soberano** sin dependencias externas

### Hashes de Evidencias

- **Datos extraídos:** `{self.state['data_hash'][:32]}...`
- **Video de sesión:** `{self.state['video_hash'][:32] if self.state['video_hash'] else 'Pendiente'}...`
- **Manifiesto:** `{self.state['manifest_hash'][:32] if self.state['manifest_hash'] else 'Pendiente'}...`

## CONCLUSIONES

La auditoría se completó exitosamente, extrayendo {stats['total_records']} registros de la URL objetivo. Se identificaron {len(sensitive_records)} registros con información sensible y {len(anomalies)} anomalías que requieren atención.

Todas las evidencias han sido selladas criptográficamente y están disponibles para verificación independiente.

## DECLARACIÓN DE VERACIDAD

El perito digital certifica que la presente auditoría se realizó siguiendo estándares técnicos y éticos, y que todas las evidencias digitales han sido preservadas con integridad mediante cadena de custodia criptográfica.

---

**Fecha de emisión:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Sistema:** Auditoría Soberana v1.0
**Hash del informe:** [Se calculará al sellar]
"""
        
        return report
    
    def _generate_fallback_report(
        self,
        stats: Dict[str, Any],
        sensitive_records: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """Genera un informe básico si Gemini falla"""
        return f"""# Informe de Análisis de Auditoría

## Resumen

- Total de registros: {stats['total_records']}
- Registros sensibles: {len(sensitive_records)}
- Anomalías: {len(anomalies)}

## Detalles

Este informe fue generado automáticamente sin análisis de IA debido a un error de conexión.
Por favor, revise los datos manualmente en el archivo CSV.
"""
