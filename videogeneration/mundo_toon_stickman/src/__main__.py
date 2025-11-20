#!/usr/bin/env python3
"""
Pipeline Completo: Mundo Toon Stickman
======================================

Orquestador maestro que ejecuta todo el flujo de trabajo:
1. Análisis de video
2. Generación de narrativa
3. Generación de animación
4. Composición de video final

Uso:
    python3 -m mundo_toon_stickman <URL_o_ruta_del_video>

Autor: Manus AI
Fecha: 20 de noviembre de 2025
"""

import sys
import json
from pathlib import Path

# Importar módulos del sistema
from src.video_analyzer import VideoAnalyzer
from src.narrative_generator import NarrativeGenerator
from src.enhanced_animator import EnhancedStickmanAnimator
from src.video_composer import VideoComposer


def main():
    """Función principal del pipeline."""
    
    if len(sys.argv) < 2:
        print("="*80)
        print("MUNDO TOON STICKMAN - Sistema de Generación de Videos Explicativos")
        print("="*80)
        print()
        print("Uso:")
        print("  python3 -m mundo_toon_stickman <URL_o_ruta_del_video> [video_id]")
        print()
        print("Ejemplos:")
        print("  python3 -m mundo_toon_stickman https://youtube.com/watch?v=...")
        print("  python3 -m mundo_toon_stickman /ruta/al/video.mp4 mi_video")
        print()
        sys.exit(1)
    
    url_or_path = sys.argv[1]
    video_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("="*80)
    print("🌟 MUNDO TOON STICKMAN - Pipeline Completo")
    print("="*80)
    print(f"📹 Entrada: {url_or_path}")
    print()
    
    # ========================================================================
    # FASE 1: Análisis de Video
    # ========================================================================
    print("🔹 FASE 1/4: Análisis de Video")
    print("-" * 80)
    
    analyzer = VideoAnalyzer()
    analysis = analyzer.analyze_video(url_or_path, video_id)
    
    video_id = analysis["video_id"]
    video_path = analysis["video_path"]
    transcript = analysis["transcript"]
    people_detections = analysis["people_detections"]
    
    print(f"✅ Análisis completado")
    print(f"   Video ID: {video_id}")
    print(f"   Duración: {analysis['metadata']['duration_seconds']:.2f}s")
    print(f"   Personas detectadas: {analysis['metadata']['total_people_detected']}")
    print()
    
    # ========================================================================
    # FASE 2: Generación de Narrativa
    # ========================================================================
    print("🔹 FASE 2/4: Generación de Narrativa Irónica")
    print("-" * 80)
    
    generator = NarrativeGenerator()
    
    # Cargar el análisis guardado
    analysis_path = f"output/transcripts/{video_id}_analysis.json"
    narrative_result = generator.process_video_analysis(analysis_path)
    
    script = narrative_result["script"]
    
    print(f"✅ Narrativa y guion completados")
    print(f"   Escenas: {len(script.get('scenes', []))}")
    print(f"   Duración: {script.get('duration_seconds', 0):.2f}s")
    print()
    
    # ========================================================================
    # FASE 3: Generación de Animación
    # ========================================================================
    print("🔹 FASE 3/4: Generación de Animación")
    print("-" * 80)
    
    animator = EnhancedStickmanAnimator(
        width=1586,  # Mismo tamaño que el video original
        height=720,
        fps=60
    )
    
    frames = animator.generate_from_script(
        script,
        "output/frames",
        people_detections
    )
    
    print(f"✅ Animación completada")
    print(f"   Frames generados: {len(frames)}")
    print()
    
    # ========================================================================
    # FASE 4: Composición de Video Final
    # ========================================================================
    print("🔹 FASE 4/4: Composición de Video Final")
    print("-" * 80)
    
    composer = VideoComposer()
    
    final_video = composer.compose_final_video(
        video_path,
        frames,
        script,
        video_id,
        fps=60
    )
    
    print(f"✅ Video final completado")
    print(f"   Ruta: {final_video}")
    print()
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("="*80)
    print("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*80)
    print()
    print(f"📊 Resumen:")
    print(f"   Video ID: {video_id}")
    print(f"   Duración original: {analysis['metadata']['duration_seconds']:.2f}s")
    print(f"   Escenas generadas: {len(script.get('scenes', []))}")
    print(f"   Frames de animación: {len(frames)}")
    print(f"   Video final: {final_video}")
    print()
    print(f"💰 Costo estimado: ~$0.004")
    print()
    print(f"🎥 Para ver el video:")
    print(f"   mpv {final_video}")
    print(f"   vlc {final_video}")
    print()


if __name__ == "__main__":
    main()
