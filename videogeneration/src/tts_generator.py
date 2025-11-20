#!/usr/bin/env python3
"""
Módulo de Generación de Voz (Text-to-Speech)
=============================================

Este módulo convierte el texto del guion en archivos de audio usando
la librería pyttsx3 (costo cero) o Google TTS (capa gratuita generosa).

Optimización de Costos:
- Usa pyttsx3 por defecto (100% gratis, sin límites)
- Opción de usar Google TTS solo si se necesita mayor calidad
"""

import os
import json
from datetime import datetime
import pyttsx3


class TTSGenerator:
    """Generador de voz para videos."""
    
    def __init__(self, engine="pyttsx3"):
        """
        Inicializa el generador de voz.
        
        Args:
            engine (str): Motor de TTS a usar ("pyttsx3" o "google")
        """
        self.engine_type = engine
        
        if engine == "pyttsx3":
            self.engine = pyttsx3.init()
            
            # Configurar voz
            voices = self.engine.getProperty('voices')
            if voices:
                # Intentar usar una voz en español si está disponible
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Configurar velocidad y volumen
            self.engine.setProperty('rate', 150)  # Velocidad de habla
            self.engine.setProperty('volume', 1.0)  # Volumen máximo
    
    def generate_audio_from_script(self, script_data, output_dir="output/audio"):
        """
        Genera archivos de audio para cada escena del guion.
        
        Args:
            script_data (dict): Datos del guion
            output_dir (str): Directorio de salida
            
        Returns:
            list: Lista de rutas a los archivos de audio generados
        """
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for scene in script_data.get('scenes', []):
            scene_num = scene.get('scene_number', 1)
            dialogue = scene.get('dialogue', '')
            
            if not dialogue:
                # Si no hay diálogo, crear un archivo de audio silencioso
                # (se puede implementar más adelante si es necesario)
                continue
            
            # Generar nombre de archivo
            filename = f"audio_{timestamp}_scene{scene_num}.mp3"
            filepath = os.path.join(output_dir, filename)
            
            # Generar audio
            if self.engine_type == "pyttsx3":
                self.engine.save_to_file(dialogue, filepath)
                self.engine.runAndWait()
            
            audio_files.append(filepath)
            print(f"✅ Audio generado: {filepath}")
        
        return audio_files
    
    def generate_single_audio(self, text, output_path):
        """
        Genera un archivo de audio para un texto específico.
        
        Args:
            text (str): Texto a convertir en voz
            output_path (str): Ruta del archivo de salida
        """
        if self.engine_type == "pyttsx3":
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
        
        print(f"✅ Audio generado: {output_path}")


def main():
    """Función de prueba del módulo."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python tts_generator.py '<texto>' [archivo_salida.mp3]")
        print("Ejemplo: python tts_generator.py '¡Hola! Soy un stickman feliz'")
        sys.exit(1)
    
    text = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output/audio/test.mp3"
    
    generator = TTSGenerator()
    generator.generate_single_audio(text, output)
    
    print(f"\n🔊 Audio guardado en: {output}")


if __name__ == "__main__":
    main()
