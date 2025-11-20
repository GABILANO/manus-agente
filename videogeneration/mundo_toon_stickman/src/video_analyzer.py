#!/usr/bin/env python3
"""
Módulo de Análisis de Video: Mundo Toon Stickman
=================================================

Este módulo se encarga de:
1. Descargar videos desde URLs (YouTube, etc.)
2. Extraer audio y transcribirlo
3. Detectar personas en el video
4. Analizar la escena y extraer metadatos

Autor: Manus AI
Fecha: 20 de noviembre de 2025
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile


class VideoAnalyzer:
    """
    Analiza videos para extraer transcripciones y metadatos de escena.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el analizador de video.
        
        Args:
            output_dir: Directorio base para guardar archivos
        """
        self.output_dir = Path(output_dir)
        self.downloads_dir = self.output_dir / "downloads"
        self.transcripts_dir = self.output_dir / "transcripts"
        
        # Crear directorios
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, url: str, video_id: Optional[str] = None) -> str:
        """
        Descarga un video desde una URL usando yt-dlp.
        
        Args:
            url: URL del video
            video_id: ID opcional para nombrar el archivo
            
        Returns:
            Ruta al archivo de video descargado
        """
        print(f"📥 Descargando video desde: {url}")
        
        # Generar nombre de archivo
        if video_id is None:
            video_id = f"video_{len(list(self.downloads_dir.glob('*.mp4')))}"
        
        output_path = self.downloads_dir / f"{video_id}.mp4"
        
        # Comando yt-dlp
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]",  # Mejor calidad en MP4
            "-o", str(output_path),
            url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video descargado: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al descargar video: {e}")
            raise
    
    def transcribe_video(self, video_path: str) -> Dict:
        """
        Transcribe el audio de un video usando manus-speech-to-text.
        
        Args:
            video_path: Ruta al archivo de video
            
        Returns:
            Diccionario con la transcripción y metadatos
        """
        print(f"🎤 Transcribiendo video: {video_path}")
        
        # Ejecutar manus-speech-to-text
        cmd = ["manus-speech-to-text", video_path]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Buscar el archivo JSON generado
            video_name = Path(video_path).stem
            transcript_files = list(Path(video_path).parent.glob(f"{video_name}_transcription_*.json"))
            
            if not transcript_files:
                raise FileNotFoundError("No se encontró el archivo de transcripción")
            
            # Leer el archivo más reciente
            latest_transcript = max(transcript_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_transcript, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
            
            # Copiar a nuestro directorio de transcripciones
            output_path = self.transcripts_dir / f"{video_name}_transcript.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Transcripción completada: {output_path}")
            
            return transcript_data
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al transcribir video: {e}")
            raise
    
    def detect_people(self, video_path: str, sample_frames: int = 10) -> List[Dict]:
        """
        Detecta personas en el video usando OpenCV.
        
        Args:
            video_path: Ruta al archivo de video
            sample_frames: Número de frames a analizar
            
        Returns:
            Lista de detecciones con posiciones
        """
        print(f"👥 Detectando personas en el video...")
        
        try:
            import cv2
        except ImportError:
            print("⚠️  OpenCV no está instalado. Instalando...")
            subprocess.run(["pip3", "install", "opencv-python"], check=True)
            import cv2
        
        # Abrir el video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {video_path}")
        
        # Obtener propiedades del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"   Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
        
        # Cargar el clasificador de rostros de Haar Cascade
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Seleccionar frames a analizar
        frame_indices = [int(i * total_frames / sample_frames) for i in range(sample_frames)]
        
        detections = []
        
        for frame_idx in frame_indices:
            # Ir al frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostros
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Guardar detecciones
            timestamp = frame_idx / fps
            
            for (x, y, w, h) in faces:
                detections.append({
                    "frame": frame_idx,
                    "timestamp": timestamp,
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "center_x": int(x + w/2),
                    "center_y": int(y + h/2)
                })
        
        cap.release()
        
        print(f"✅ Detectadas {len(detections)} personas en {sample_frames} frames")
        
        return detections
    
    def analyze_video(self, url_or_path: str, video_id: Optional[str] = None) -> Dict:
        """
        Análisis completo de un video: descarga, transcripción y detección.
        
        Args:
            url_or_path: URL o ruta local del video
            video_id: ID opcional para nombrar archivos
            
        Returns:
            Diccionario con todos los datos del análisis
        """
        print("="*80)
        print("🎬 ANÁLISIS DE VIDEO: Mundo Toon Stickman")
        print("="*80)
        print()
        
        # Determinar si es URL o ruta local
        if url_or_path.startswith(("http://", "https://")):
            video_path = self.download_video(url_or_path, video_id)
        else:
            video_path = url_or_path
            print(f"📂 Usando video local: {video_path}")
        
        print()
        
        # Transcribir
        transcript = self.transcribe_video(video_path)
        
        print()
        
        # Detectar personas
        people_detections = self.detect_people(video_path)
        
        print()
        
        # Compilar resultados
        analysis = {
            "video_path": video_path,
            "video_id": video_id or Path(video_path).stem,
            "transcript": transcript,
            "people_detections": people_detections,
            "metadata": {
                "total_people_detected": len(people_detections),
                "duration_seconds": transcript.get("duration", 0),
                "language": transcript.get("language", "unknown")
            }
        }
        
        # Guardar análisis completo
        analysis_path = self.transcripts_dir / f"{analysis['video_id']}_analysis.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Análisis guardado: {analysis_path}")
        print()
        print("="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80)
        print()
        
        return analysis


def main():
    """Función principal para pruebas."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 video_analyzer.py <URL_o_ruta_del_video>")
        sys.exit(1)
    
    url_or_path = sys.argv[1]
    video_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = VideoAnalyzer()
    analysis = analyzer.analyze_video(url_or_path, video_id)
    
    print(f"📊 Resumen del análisis:")
    print(f"   Duración: {analysis['metadata']['duration_seconds']:.2f} segundos")
    print(f"   Idioma: {analysis['metadata']['language']}")
    print(f"   Personas detectadas: {analysis['metadata']['total_people_detected']}")


if __name__ == "__main__":
    main()
