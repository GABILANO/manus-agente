#!/usr/bin/env python3
"""
Módulo de Ensamblaje de Video
==============================

Este módulo ensambla los frames y audio en un video final usando MoviePy.

Optimización de Costos:
- 100% código Python con MoviePy (gratis)
- Renderizado local en Manus
- Sin costos de procesamiento en la nube
"""

import os
from datetime import datetime
from moviepy import ImageSequenceClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips


class VideoAssembler:
    """Ensamblador de videos a partir de frames y audio."""
    
    def __init__(self, fps=10):
        """
        Inicializa el ensamblador.
        
        Args:
            fps (int): Frames por segundo del video final
        """
        self.fps = fps
    
    def assemble_video(self, frames, audio_files=None, output_path=None):
        """
        Ensambla un video a partir de frames y audio.
        
        Args:
            frames (list): Lista de rutas a los frames (imágenes PNG)
            audio_files (list): Lista de rutas a archivos de audio (opcional)
            output_path (str): Ruta del video de salida
            
        Returns:
            str: Ruta del video generado
        """
        if not frames:
            raise ValueError("Se requiere al menos un frame para crear el video")
        
        # Crear clip de video desde los frames
        print(f"🎬 Ensamblando video con {len(frames)} frames...")
        video_clip = ImageSequenceClip(frames, fps=self.fps)
        
        # Añadir audio si está disponible
        if audio_files and len(audio_files) > 0:
            print(f"🔊 Añadiendo {len(audio_files)} pistas de audio...")
            
            # Por ahora, usar solo el primer archivo de audio
            # TODO: Concatenar múltiples audios si hay varias escenas
            if os.path.exists(audio_files[0]):
                audio_clip = AudioFileClip(audio_files[0])
                
                # Ajustar duración del video al audio
                if audio_clip.duration > video_clip.duration:
                    video_clip = video_clip.loop(duration=audio_clip.duration)
                elif audio_clip.duration < video_clip.duration:
                    video_clip = video_clip.set_duration(audio_clip.duration)
                
                video_clip = video_clip.set_audio(audio_clip)
        
        # Generar ruta de salida si no se proporciona
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "output/videos"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"video_{timestamp}.mp4")
        
        # Renderizar video
        print(f"⚙️  Renderizando video...")
        video_clip.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        
        print(f"✅ Video generado: {output_path}")
        return output_path
    
    def assemble_from_script_data(self, script_data, frames, audio_files=None, output_path=None):
        """
        Ensambla un video usando los datos del guion.
        
        Args:
            script_data (dict): Datos del guion
            frames (list): Lista de rutas a los frames
            audio_files (list): Lista de rutas a archivos de audio (opcional)
            output_path (str): Ruta del video de salida
            
        Returns:
            str: Ruta del video generado
        """
        title = script_data.get('title', 'Video sin título')
        print(f"\n🎥 Ensamblando video: {title}")
        
        return self.assemble_video(frames, audio_files, output_path)


def main():
    """Función de prueba del módulo."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python video_assembler.py <directorio_frames> [archivo_audio.mp3]")
        print("Ejemplo: python video_assembler.py output/frames/ output/audio/audio.mp3")
        sys.exit(1)
    
    frames_dir = sys.argv[1]
    audio_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Obtener lista de frames
    import glob
    frames = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    
    if not frames:
        print(f"❌ No se encontraron frames en {frames_dir}")
        sys.exit(1)
    
    print(f"📁 Encontrados {len(frames)} frames")
    
    # Ensamblar video
    assembler = VideoAssembler(fps=10)
    audio_files = [audio_file] if audio_file else None
    video_path = assembler.assemble_video(frames, audio_files)
    
    print(f"\n✅ Video final: {video_path}")


if __name__ == "__main__":
    main()
