"""
Módulo de Estado del Agente de Auditoría Soberana
Implementa el AgentState para LangGraph basado en el modelo MDP
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AuditStatus(str, Enum):
    """Estados posibles de una auditoría"""
    INITIALIZED = "initialized"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    SEALING = "sealing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(TypedDict):
    """
    Estado persistente del agente de auditoría que fluye a través de LangGraph.
    Implementa la Propiedad de Markov: toda la información necesaria para
    decidir la próxima acción está contenida en este estado.
    """
    
    # Identificación de la auditoría
    audit_id: str
    timestamp: str
    
    # Objetivo y configuración
    user_prompt: str
    target_url: str
    audit_depth: int  # Nivel de profundidad de la auditoría (1-5)
    
    # Estado de la ejecución
    status: AuditStatus
    current_task: str
    
    # Rutas a artefactos generados
    output_dir: str
    extracted_data_path: Optional[str]
    video_evidence_path: Optional[str]
    screenshots_dir: Optional[str]
    log_path: Optional[str]
    manifest_path: Optional[str]
    
    # Datos extraídos (en memoria para procesamiento)
    extracted_records: List[Dict[str, Any]]
    total_records: int
    
    # Análisis y clasificación
    sensitive_records: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    
    # Cadena de custodia criptográfica
    data_hash: Optional[str]
    video_hash: Optional[str]
    log_hash: Optional[str]
    manifest_hash: Optional[str]
    chain_of_custody: List[Dict[str, str]]
    
    # Informes generados
    analysis_report_path: Optional[str]
    forensic_report_path: Optional[str]
    summary_report_path: Optional[str]
    
    # Metadatos de ejecución
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    
    # Errores y logs
    errors: List[str]
    warnings: List[str]


def create_initial_state(user_prompt: str, target_url: str, audit_depth: int = 3) -> AgentState:
    """
    Crea el estado inicial de una nueva auditoría.
    
    Args:
        user_prompt: Descripción del objetivo de la auditoría
        target_url: URL del sitio a auditar
        audit_depth: Profundidad de la auditoría (1=superficial, 5=exhaustiva)
    
    Returns:
        AgentState inicializado
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audit_id = f"audit_{timestamp}"
    
    return AgentState(
        audit_id=audit_id,
        timestamp=timestamp,
        user_prompt=user_prompt,
        target_url=target_url,
        audit_depth=audit_depth,
        status=AuditStatus.INITIALIZED,
        current_task="Inicializando auditoría",
        output_dir=f"/home/ubuntu/manus-agente/audit-system/audits/{audit_id}",
        extracted_data_path=None,
        video_evidence_path=None,
        screenshots_dir=None,
        log_path=None,
        manifest_path=None,
        extracted_records=[],
        total_records=0,
        sensitive_records=[],
        anomalies=[],
        data_hash=None,
        video_hash=None,
        log_hash=None,
        manifest_hash=None,
        chain_of_custody=[],
        analysis_report_path=None,
        forensic_report_path=None,
        summary_report_path=None,
        start_time=None,
        end_time=None,
        duration_seconds=None,
        errors=[],
        warnings=[]
    )
