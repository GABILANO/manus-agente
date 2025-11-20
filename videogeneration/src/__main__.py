#!/usr/bin/env python3
"""
Sistema de Generación de Video Costo-Optimizado
================================================

Script principal que orquesta todo el proceso de generación de video:
1. Generación de guion con Gemini AI
2. Generación de voz con TTS
3. Generación de frames con animación stickman
4. Ensamblaje de video con MoviePy

Uso:
    python -m videogeneration.src '<prompt>' [--duration SEGUNDOS] [--output RUTA]

Ejemplo:
    python -m videogeneration.src 'Un stickman bailando feliz' --duration 10
"""

import sys
import os
import argparse
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.script_generator import ScriptGenerator
from src.tts_generator import TTSGenerator
from src.scene_generator import StickmanAnimator
from src.video_assembler import VideoAssembler


class VideoGenerationPipeline:
    """Pipeline completo de generación de video."""
    
    def __init__(self, base_dir=None):
        """
        Inicializa el pipeline.
        
        Args:
            base_dir (str): Directorio base del proyecto
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "output"
        
        # Crear directorios de salida
        (self.output_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "audio").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "frames").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "videos").mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.script_gen = ScriptGenerator()
        self.tts_gen = TTSGenerator(engine="pyttsx3")
        self.animator = StickmanAnimator(width=640, height=480, fps=10)
        self.assembler = VideoAssembler(fps=10)
    
    def generate_video(self, prompt, duration_seconds=10, style="stickman", output_path=None):
        """
        Genera un video completo a partir de un prompt.
        
        Args:
            prompt (str): Descripción del video deseado
            duration_seconds (int): Duración del video en segundos
            style (str): Estilo de animación
            output_path (str): Ruta del video de salida (opcional)
            
        Returns:
            str: Ruta del video generado
        """
        print("="*80)
        print("🎬 SISTEMA DE GENERACIÓN DE VIDEO COSTO-OPTIMIZADO")
        print("="*80)
        print(f"\n📝 Prompt: {prompt}")
        print(f"⏱️  Duración: {duration_seconds} segundos")
        print(f"🎨 Estilo: {style}")
        print()
        
        # ETAPA 1: Generar guion
        print("="*80)
        print("ETAPA 1: Generación de Guion con Gemini AI")
        print("="*80)
        script_data = self.script_gen.generate_script(
            prompt=prompt,
            duration_seconds=duration_seconds,
            style=style
        )
        script_path = self.script_gen.save_script(
            script_data,
            output_dir=str(self.output_dir / "scripts")
        )
        print(f"✅ Guion generado: {script_path}")
        print()
        
        # ETAPA 2: Generar voz
        print("="*80)
        print("ETAPA 2: Generación de Voz (Text-to-Speech)")
        print("="*80)
        audio_files = self.tts_gen.generate_audio_from_script(
            script_data,
            output_dir=str(self.output_dir / "audio")
        )
        if audio_files:
            print(f"✅ Generados {len(audio_files)} archivos de audio")
        else:
            print("ℹ️  No se generó audio (sin diálogos en el guion)")
        print()
        
        # ETAPA 3: Generar frames
        print("="*80)
        print("ETAPA 3: Generación de Frames (Animación)")
        print("="*80)
        frames = self.animator.generate_frames_from_script(
            script_data,
            output_dir=str(self.output_dir / "frames")
        )
        print(f"✅ Generados {len(frames)} frames")
        print()
        
        # ETAPA 4: Ensamblar video
        print("="*80)
        print("ETAPA 4: Ensamblaje de Video")
        print("="*80)
        video_path = self.assembler.assemble_from_script_data(
            script_data,
            frames=frames,
            audio_files=audio_files if audio_files else None,
            output_path=output_path
        )
        print()
        
        # Resumen final
        print("="*80)
        print("✅ GENERACIÓN COMPLETADA")
        print("="*80)
        print(f"\n🎥 Video final: {video_path}")
        print(f"📊 Guion: {script_path}")
        print(f"🎨 Frames: {len(frames)}")
        print(f"🔊 Audio: {len(audio_files) if audio_files else 0} archivos")
        print()
        print("💡 Puedes ver el video con:")
        print(f"   mpv {video_path}")
        print(f"   vlc {video_path}")
        print()
        
        return video_path


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Generación de Video Costo-Optimizado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python -m videogeneration.src 'Un stickman bailando feliz'
  python -m videogeneration.src 'Stickman haciendo ejercicio' --duration 15
  python -m videogeneration.src 'Aventura de un stickman' --output mi_video.mp4
        """
    )
    
    parser.add_argument(
        'prompt',
        type=str,
        help='Descripción del video que deseas generar'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Duración del video en segundos (default: 10)'
    )
    
    parser.add_argument(
        '--style',
        type=str,
        default='stickman',
        choices=['stickman'],
        help='Estilo de animación (default: stickman)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Ruta del video de salida (opcional)'
    )
    
    args = parser.parse_args()
    
    # Crear pipeline y generar video
    pipeline = VideoGenerationPipeline()
    
    try:
        video_path = pipeline.generate_video(
            prompt=args.prompt,
            duration_seconds=args.duration,
            style=args.style,
            output_path=args.output
        )
        
        print("🎉 ¡Generación exitosa!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
