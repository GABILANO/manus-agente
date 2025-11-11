#!/usr/bin/env python3
"""
Sistema de Auditoría Soberana
Punto de entrada principal para ejecutar auditorías web
"""

import sys
import argparse
from pathlib import Path

# Añadir el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import AuditOrchestrator


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Sistema de Auditoría Soberana - Auditoría profesional de sitios web con evidencia criptográfica'
    )
    
    parser.add_argument(
        'url',
        type=str,
        help='URL del sitio web a auditar'
    )
    
    parser.add_argument(
        '-p', '--prompt',
        type=str,
        default='Auditoría general del sitio web',
        help='Descripción del objetivo de la auditoría'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help='Profundidad de la auditoría (1=superficial, 5=exhaustiva)'
    )
    
    args = parser.parse_args()
    
    try:
        # Crear orquestador
        orchestrator = AuditOrchestrator()
        
        # Ejecutar auditoría
        final_state = orchestrator.run_audit(
            user_prompt=args.prompt,
            target_url=args.url,
            audit_depth=args.depth
        )
        
        # Mostrar resultados
        print("\n" + "="*80)
        print("RESULTADOS DE LA AUDITORÍA")
        print("="*80)
        print(f"\n📁 Directorio de salida: {final_state['output_dir']}")
        print(f"\n📊 Registros extraídos: {final_state['total_records']}")
        print(f"🔒 Registros sensibles: {len(final_state['sensitive_records'])}")
        print(f"⚠️  Anomalías: {len(final_state['anomalies'])}")
        
        print(f"\n📄 Informes generados:")
        print(f"   - Resumen: {final_state['summary_report_path']}")
        print(f"   - Análisis: {final_state['analysis_report_path']}")
        print(f"   - Pericial: {final_state['forensic_report_path']}")
        
        print(f"\n🎥 Video de evidencia: {final_state['video_evidence_path']}")
        print(f"🔐 Manifiesto: {final_state['manifest_path']}")
        print(f"   Hash: {final_state['manifest_hash'][:32]}...")
        
        if final_state['errors']:
            print(f"\n❌ Errores ({len(final_state['errors'])}):")
            for error in final_state['errors']:
                print(f"   - {error}")
        
        print("\n" + "="*80)
        print("✅ Auditoría completada exitosamente")
        print("="*80 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Auditoría interrumpida por el usuario")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
