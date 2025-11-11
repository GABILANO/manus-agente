"""
Orquestador Principal del Sistema de Auditoría
Implementa el grafo de estados con LangGraph
"""

import os
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from core.state import AgentState, AuditStatus, create_initial_state
from agents.evidence_collector import EvidenceCollectorAgent
from agents.crypto_forensics import CryptoForensicsAgent
from agents.data_analyst import DataAnalysisAgent


class AuditOrchestrator:
    """
    Orquestador que coordina todos los agentes usando LangGraph.
    Implementa el flujo de auditoría como un Proceso de Decisión de Markov (MDP).
    """
    
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")
        
        # Construir el grafo de estados
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Construye el grafo de estados de LangGraph.
        Define los nodos (agentes) y las transiciones entre ellos.
        """
        # Crear grafo
        workflow = StateGraph(AgentState)
        
        # Añadir nodos (cada nodo es un agente)
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("collect_evidence", self._collect_evidence_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("seal_evidence", self._seal_evidence_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Definir el flujo (transiciones)
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "collect_evidence")
        workflow.add_edge("collect_evidence", "analyze_data")
        workflow.add_edge("analyze_data", "seal_evidence")
        workflow.add_edge("seal_evidence", "finalize")
        workflow.add_edge("finalize", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def run_audit(self, user_prompt: str, target_url: str, audit_depth: int = 3) -> AgentState:
        """
        Ejecuta una auditoría completa.
        
        Args:
            user_prompt: Descripción del objetivo de la auditoría
            target_url: URL del sitio a auditar
            audit_depth: Profundidad de la auditoría (1-5)
        
        Returns:
            Estado final de la auditoría con todos los resultados
        """
        print(f"\n{'='*80}")
        print(f"INICIANDO AUDITORÍA SOBERANA")
        print(f"{'='*80}")
        print(f"Objetivo: {user_prompt}")
        print(f"URL: {target_url}")
        print(f"Profundidad: {audit_depth}")
        print(f"{'='*80}\n")
        
        # Crear estado inicial
        initial_state = create_initial_state(user_prompt, target_url, audit_depth)
        
        # Ejecutar el grafo
        final_state = self.graph.invoke(initial_state)
        
        return final_state
    
    # ===== NODOS DEL GRAFO =====
    
    def _initialize_node(self, state: AgentState) -> AgentState:
        """Nodo de inicialización"""
        print("\n[Orchestrator] FASE 1: Inicialización")
        
        # Crear directorio de salida
        os.makedirs(state['output_dir'], exist_ok=True)
        
        # Crear archivo de log
        log_path = os.path.join(state['output_dir'], 'audit.log')
        state['log_path'] = log_path
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"=== AUDITORÍA SOBERANA ===\n")
            f.write(f"ID: {state['audit_id']}\n")
            f.write(f"Inicio: {datetime.now().isoformat()}\n")
            f.write(f"URL: {state['target_url']}\n")
            f.write(f"Objetivo: {state['user_prompt']}\n")
            f.write(f"{'='*50}\n\n")
        
        state['start_time'] = datetime.now()
        
        print(f"[Orchestrator] Directorio de salida: {state['output_dir']}")
        print(f"[Orchestrator] Log: {log_path}")
        
        return state
    
    def _collect_evidence_node(self, state: AgentState) -> AgentState:
        """Nodo de recolección de evidencias"""
        print("\n[Orchestrator] FASE 2: Recolección de Evidencias")
        
        # Ejecutar agente recolector
        import asyncio
        agent = EvidenceCollectorAgent(state)
        state = asyncio.run(agent.execute())
        
        # Registrar en log
        self._log_event(state, f"Evidencias recolectadas: {state['total_records']} registros")
        
        return state
    
    def _analyze_data_node(self, state: AgentState) -> AgentState:
        """Nodo de análisis de datos"""
        print("\n[Orchestrator] FASE 3: Análisis de Datos")
        
        # Ejecutar agente analista
        agent = DataAnalysisAgent(state, self.gemini_api_key)
        state = agent.execute()
        
        # Registrar en log
        self._log_event(
            state, 
            f"Análisis completado: {len(state['sensitive_records'])} registros sensibles, "
            f"{len(state['anomalies'])} anomalías"
        )
        
        return state
    
    def _seal_evidence_node(self, state: AgentState) -> AgentState:
        """Nodo de sellado criptográfico"""
        print("\n[Orchestrator] FASE 4: Sellado Criptográfico")
        
        # Ejecutar agente forense
        agent = CryptoForensicsAgent(state)
        state = agent.execute()
        
        # Registrar en log
        self._log_event(state, f"Evidencias selladas. Hash del manifiesto: {state['manifest_hash']}")
        
        return state
    
    def _finalize_node(self, state: AgentState) -> AgentState:
        """Nodo de finalización"""
        print("\n[Orchestrator] FASE 5: Finalización")
        
        state['end_time'] = datetime.now()
        state['duration_seconds'] = (state['end_time'] - state['start_time']).total_seconds()
        state['status'] = AuditStatus.COMPLETED
        state['current_task'] = "Auditoría completada"
        
        # Generar resumen final
        summary = self._generate_summary(state)
        summary_path = os.path.join(state['output_dir'], 'RESUMEN.md')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        state['summary_report_path'] = summary_path
        
        # Registrar en log
        self._log_event(state, f"Auditoría completada en {state['duration_seconds']:.2f} segundos")
        
        print(f"\n{'='*80}")
        print(f"AUDITORÍA COMPLETADA EXITOSAMENTE")
        print(f"{'='*80}")
        print(f"Duración: {state['duration_seconds']:.2f} segundos")
        print(f"Registros extraídos: {state['total_records']}")
        print(f"Registros sensibles: {len(state['sensitive_records'])}")
        print(f"Directorio de salida: {state['output_dir']}")
        print(f"{'='*80}\n")
        
        return state
    
    def _log_event(self, state: AgentState, message: str):
        """Registra un evento en el log de auditoría"""
        if state['log_path']:
            with open(state['log_path'], 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
    
    def _generate_summary(self, state: AgentState) -> str:
        """Genera el resumen ejecutivo de la auditoría"""
        summary = f"""# RESUMEN EJECUTIVO DE AUDITORÍA

## Identificación

- **ID de Auditoría:** {state['audit_id']}
- **Fecha:** {state['timestamp']}
- **Duración:** {state['duration_seconds']:.2f} segundos
- **Estado:** {state['status']}

## Objetivo

{state['user_prompt']}

## URL Auditada

{state['target_url']}

## Resultados Clave

| Métrica | Valor |
|---------|-------|
| Registros extraídos | {state['total_records']} |
| Registros sensibles | {len(state['sensitive_records'])} |
| Anomalías detectadas | {len(state['anomalies'])} |
| Errores | {len(state['errors'])} |
| Advertencias | {len(state['warnings'])} |

## Evidencias Generadas

- ✅ **Datos extraídos:** `extracted_data.csv`
- ✅ **Video de sesión:** `audit_session.webm`
- ✅ **Screenshots:** {len(os.listdir(state['screenshots_dir'])) if state['screenshots_dir'] and os.path.exists(state['screenshots_dir']) else 0} capturas
- ✅ **Informe de análisis:** `informe_analisis.md`
- ✅ **Informe pericial:** `informe_pericial.md`
- ✅ **Manifiesto criptográfico:** `manifest.json`

## Cadena de Custodia

Todas las evidencias han sido selladas criptográficamente con SHA-256.

**Hash del Manifiesto:** `{state['manifest_hash']}`

## Verificación de Integridad

Para verificar la integridad de esta auditoría:

```bash
# Verificar hash del manifiesto
sha256sum manifest.json

# Verificar hash de datos
sha256sum extracted_data.csv

# Verificar hash de video
sha256sum audit_session.webm
```

Los hashes deben coincidir con los registrados en el manifiesto.

## Archivos del Informe

1. **Este resumen:** `RESUMEN.md`
2. **Informe de análisis detallado:** `informe_analisis.md`
3. **Informe pericial forense:** `informe_pericial.md`
4. **Datos en formato CSV:** `extracted_data.csv`
5. **Video de evidencia:** `audit_session.webm`
6. **Manifiesto criptográfico:** `manifest.json`

## Conclusión

La auditoría se completó {'exitosamente' if state['status'] == AuditStatus.COMPLETED else 'con errores'}.
Todas las evidencias están disponibles en: `{state['output_dir']}`

---

**Sistema de Auditoría Soberana v1.0**
**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return summary
