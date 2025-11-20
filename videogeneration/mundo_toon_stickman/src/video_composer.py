#!/usr/bin/env python3
"""
Módulo de Composición de Video: Mundo Toon Stickman
====================================================

Este módulo se encarga de:
1. Generar audio TTS desde el guion
2. Sincronizar frames de animación con audio
3. Componer video final (overlay sobre video original)
4. Aplicar efectos y transiciones

Autor: Manus AI
Fecha: 20 de noviembre de 2025
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import pyttsx3


class VideoComposer:
    """
    Compone el video final combinando animación, audio y video base.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el compositor de video.
        
        Args:
            output_dir: Directorio base para guardar archivos
        """
        self.output_dir = Path(output_dir)
        self.audio_dir = self.output_dir / "audio"
        self.final_videos_dir = self.output_dir / "final_videos"
        
        # Crear directorios
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.final_videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Velocidad de habla
        self.tts_engine.setProperty('volume', 1.0)  # Volumen
    
    def generate_audio_from_script(self, script: Dict, video_id: str) -> List[str]:
        """
        Genera archivos de audio desde el guion.
        
        Args:
            script: Guion completo
            video_id: ID del video
            
        Returns:
            Lista de rutas a los archivos de audio
        """
        print("🎤 Generando audio desde guion...")
        
        audio_files = []
        scenes = script.get("scenes", [])
        
        for scene in scenes:
            scene_num = scene.get("scene_number", 1)
            dialogue = scene.get("dialogue", "")
            
            if not dialogue:
                continue
            
            # Generar audio para este diálogo
            audio_path = self.audio_dir / f"{video_id}_scene{scene_num}.mp3"
            
            self.tts_engine.save_to_file(dialogue, str(audio_path))
            self.tts_engine.runAndWait()
            
            audio_files.append(str(audio_path))
            print(f"   ✅ Audio generado para escena {scene_num}")
        
        print(f"✅ Total de audios generados: {len(audio_files)}")
        return audio_files
    
    def create_animation_video(
        self,
        frames: List[str],
        fps: int,
        output_path: str
    ) -> str:
        """
        Crea un video desde frames de animación.
        
        Args:
            frames: Lista de rutas a frames
            fps: Frames por segundo
            output_path: Ruta de salida
            
        Returns:
            Ruta al video generado
        """
        print("🎬 Creando video de animación desde frames...")
        
        # Crear archivo de lista de frames
        frames_list_path = Path(output_path).parent / "frames_list.txt"
        with open(frames_list_path, 'w') as f:
            for frame in frames:
                # Usar ruta absoluta
                abs_frame = str(Path(frame).absolute())
                f.write(f"file '{abs_frame}'\n")
                f.write(f"duration {1/fps}\n")
        
        # Comando FFmpeg para crear video desde frames
        cmd = [
            "ffmpeg",
            "-y",  # Sobrescribir sin preguntar
            "-f", "concat",
            "-safe", "0",
            "-i", str(frames_list_path),
            "-vf", f"fps={fps}",
            "-c:v", "libx264",
            "-pix_fmt", "yuva420p",  # Soporte para canal alfa
            "-preset", "fast",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video de animación creado: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al crear video: {e}")
            print(f"Stderr: {e.stderr.decode()}")
            raise
    
    def overlay_animation_on_video(
        self,
        base_video: str,
        animation_video: str,
        output_path: str,
        opacity: float = 0.7
    ) -> str:
        """
        Superpone la animación sobre el video base.
        
        Args:
            base_video: Ruta al video original
            animation_video: Ruta al video de animación
            output_path: Ruta de salida
            opacity: Opacidad del video base (0-1)
            
        Returns:
            Ruta al video compuesto
        """
        print("🎨 Superponiendo animación sobre video base...")
        
        # Comando FFmpeg para overlay
        cmd = [
            "ffmpeg",
            "-y",
            "-i", base_video,
            "-i", animation_video,
            "-filter_complex",
            f"[0:v]format=yuva420p,colorchannelmixer=aa={opacity}[base];"
            f"[base][1:v]overlay=0:0[out]",
            "-map", "[out]",
            "-map", "0:a?",  # Audio del video base (si existe)
            "-c:v", "libx264",
            "-c:a", "copy",
            "-preset", "fast",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video compuesto creado: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al componer video: {e}")
            print(f"Stderr: {e.stderr.decode()}")
            raise
    
    def add_audio_to_video(
        self,
        video_path: str,
        audio_files: List[str],
        output_path: str
    ) -> str:
        """
        Añade audio al video.
        
        Args:
            video_path: Ruta al video
            audio_files: Lista de archivos de audio
            output_path: Ruta de salida
            
        Returns:
            Ruta al video con audio
        """
        print("🔊 Añadiendo audio al video...")
        
        if not audio_files:
            print("⚠️  No hay archivos de audio, copiando video sin cambios")
            subprocess.run(["cp", video_path, output_path], check=True)
            return output_path
        
        # Concatenar audios
        concat_audio_path = Path(output_path).parent / "concat_audio.mp3"
        
        if len(audio_files) == 1:
            # Solo un audio
            concat_audio_path = audio_files[0]
        else:
            # Solución alternativa para concatenar audios
            input_args = []
            for audio in audio_files:
                input_args.extend(["-i", str(Path(audio).absolute())])
            
            filter_complex = f"concat=n={len(audio_files)}:v=0:a=1[outa]"
            
            cmd = [
                "ffmpeg",
                "-y",
                *input_args,
                "-filter_complex", filter_complex,
                "-map", "[outa]",
                str(concat_audio_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)        
        # Añadir audio al video
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", str(concat_audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v",
            "-map", "1:a",
            "-shortest",  # Duración del más corto
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Audio añadido al video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al añadir audio: {e}")
            print(f"Stderr: {e.stderr.decode()}")
            raise
    
    def compose_final_video(
        self,
        base_video: str,
        frames: List[str],
        script: Dict,
        video_id: str,
        fps: int = 60
    ) -> str:
        """
        Compone el video final completo.
        
        Args:
            base_video: Ruta al video original
            frames: Lista de frames de animación
            script: Guion completo
            video_id: ID del video
            fps: Frames por segundo
            
        Returns:
            Ruta al video final
        """
        print("="*80)
        print("🎬 COMPOSICIÓN DE VIDEO FINAL: Mundo Toon Stickman")
        print("="*80)
        print()
        
        # Paso 1: Generar audio
        audio_files = self.generate_audio_from_script(script, video_id)
        print()
        
        # Paso 2: Crear video de animación
        animation_video_path = self.final_videos_dir / f"{video_id}_animation.mp4"
        self.create_animation_video(frames, fps, str(animation_video_path))
        print()
        
        # Paso 3: Superponer animación sobre video base
        overlay_video_path = self.final_videos_dir / f"{video_id}_overlay.mp4"
        self.overlay_animation_on_video(
            base_video,
            str(animation_video_path),
            str(overlay_video_path),
            opacity=0.7
        )
        print()
        
        # Paso 4: Añadir audio
        final_video_path = self.final_videos_dir / f"{video_id}_final.mp4"
        self.add_audio_to_video(
            str(overlay_video_path),
            audio_files,
            str(final_video_path)
        )
        print()
        
        print("="*80)
        print("✅ VIDEO FINAL COMPLETADO")
        print("="*80)
        print(f"📁 Ruta: {final_video_path}")
        print()
        
        return str(final_video_path)


def main():
    """Función principal para pruebas."""
    import sys
    
    if len(sys.argv) < 4:
        print("Uso: python3 video_composer.py <video_base> <frames_dir> <script.json>")
        sys.exit(1)
    
    base_video = sys.argv[1]
    frames_dir = sys.argv[2]
    script_path = sys.argv[3]
    
    # Cargar guion
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    
    # Obtener lista de frames
    frames = sorted(Path(frames_dir).glob("*.png"))
    frames = [str(f) for f in frames]
    
    composer = VideoComposer()
    final_video = composer.compose_final_video(
        base_video,
        frames,
        script,
        "test_corte",
        fps=60
    )
    
    print(f"✅ Video final: {final_video}")


if __name__ == "__main__":
    main()
