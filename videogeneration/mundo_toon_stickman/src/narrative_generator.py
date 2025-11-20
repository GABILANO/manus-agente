#!/usr/bin/env python3
"""
Módulo de Generación de Narrativas Irónicas: Mundo Toon Stickman
=================================================================

Este módulo utiliza Gemini AI para:
1. Analizar transcripciones y detectar contradicciones
2. Generar narrativas irónicas comprensibles para niños
3. Crear guiones estructurados para animación

Autor: Manus AI
Fecha: 20 de noviembre de 2025
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import google.generativeai as genai


class NarrativeGenerator:
    """
    Genera narrativas irónicas y guiones animados usando Gemini AI.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el generador de narrativas.
        
        Args:
            output_dir: Directorio base para guardar archivos
        """
        self.output_dir = Path(output_dir)
        self.narratives_dir = self.output_dir / "narratives"
        self.scripts_dir = self.output_dir / "scripts"
        
        # Crear directorios
        self.narratives_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar Gemini AI
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurado en las variables de entorno")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def analyze_contradictions(self, transcript: Dict) -> str:
        """
        Analiza una transcripción para detectar contradicciones e incoherencias.
        
        Args:
            transcript: Diccionario con la transcripción
            
        Returns:
            Análisis de contradicciones en texto
        """
        print("🔍 Analizando contradicciones e incoherencias...")
        
        # Extraer el texto completo
        segments = transcript.get("segments", [])
        full_text = "\n".join([
            f"[{seg.get('start', 0):.1f}s] {seg.get('text', '')}"
            for seg in segments
        ])
        
        # Prompt para análisis de contradicciones
        prompt = f"""Eres un analista experto en detectar contradicciones, falacias lógicas e incoherencias en discursos políticos y judiciales.

Analiza el siguiente texto transcrito de un video y:

1. Identifica TODAS las contradicciones, falacias e incoherencias
2. Explica por qué son problemáticas
3. Señala los momentos clave (timestamps) donde ocurren
4. Clasifica cada problema (contradicción, falacia, incoherencia, etc.)

TRANSCRIPCIÓN:
{full_text}

Proporciona un análisis detallado y estructurado."""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            print(f"✅ Análisis completado ({len(analysis)} caracteres)")
            return analysis
            
        except Exception as e:
            print(f"❌ Error al analizar contradicciones: {e}")
            raise
    
    def generate_ironic_narrative(self, transcript: Dict, analysis: str) -> str:
        """
        Genera una narrativa irónica comprensible para niños.
        
        Args:
            transcript: Diccionario con la transcripción
            analysis: Análisis de contradicciones
            
        Returns:
            Narrativa irónica en texto
        """
        print("📝 Generando narrativa irónica para niños...")
        
        # Extraer el texto completo
        segments = transcript.get("segments", [])
        full_text = "\n".join([seg.get("text", "") for seg in segments])
        
        # Prompt para narrativa irónica
        prompt = f"""Eres un escritor creativo especializado en explicar temas complejos a niños usando humor, ironía y analogías.

Tu tarea es transformar este análisis de un discurso político/judicial en una historia DIVERTIDA, IRÓNICA y EDUCATIVA que un niño de 10 años pueda entender.

REGLAS:
1. Usa analogías simples y exageradas (ej: "Es como si dijera que el cielo es verde y luego se quejara del color azul")
2. Mantén un tono irónico pero constructivo (no ofensivo)
3. Resalta las contradicciones de forma cómica
4. Usa personajes y situaciones que los niños entiendan
5. Mantén la historia corta y dinámica (máximo 200 palabras)
6. Termina con una moraleja o reflexión simple

TEXTO ORIGINAL:
{full_text}

ANÁLISIS DE CONTRADICCIONES:
{analysis}

Escribe la narrativa irónica ahora:"""
        
        try:
            response = self.model.generate_content(prompt)
            narrative = response.text
            
            print(f"✅ Narrativa generada ({len(narrative)} caracteres)")
            return narrative
            
        except Exception as e:
            print(f"❌ Error al generar narrativa: {e}")
            raise
    
    def generate_animation_script(
        self,
        narrative: str,
        transcript: Dict,
        people_count: int = 3
    ) -> Dict:
        """
        Genera un guion estructurado para animación.
        
        Args:
            narrative: Narrativa irónica
            transcript: Transcripción original
            people_count: Número de personajes en la escena
            
        Returns:
            Guion en formato JSON
        """
        print("🎬 Generando guion de animación...")
        
        duration = transcript.get("duration", 10)
        
        # Prompt para guion de animación
        prompt = f"""Eres un guionista de animación experto en sincronización y timing.

Convierte esta narrativa irónica en un GUION ESTRUCTURADO para una animación de stickman.

NARRATIVA:
{narrative}

DURACIÓN DEL VIDEO: {duration} segundos
NÚMERO DE PERSONAJES: {people_count}

FORMATO DEL GUION (devuelve SOLO JSON válido):
{{
  "title": "Título del video",
  "duration_seconds": {duration},
  "style": "stickman_ironic",
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": 0.0,
      "end_time": 2.5,
      "duration_seconds": 2.5,
      "visual_description": "Descripción de lo que se ve",
      "dialogue": "Texto que se dice",
      "character": "character_1",
      "action": "standing/waving/jumping/dancing/running/talking/thinking/surprised",
      "expression": "neutral/happy/sad/angry/confused/surprised",
      "hand_gesture": "none/pointing/waving/clapping/thinking"
    }}
  ]
}}

REGLAS:
1. Divide la narrativa en escenas de 2-4 segundos cada una
2. Asigna diálogos cortos y claros a cada escena
3. Especifica la acción y expresión de cada personaje
4. Los tiempos deben ser consecutivos y sumar {duration} segundos
5. Usa expresiones y gestos que refuercen la ironía

Genera el guion JSON ahora:"""
        
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            
            # Extraer JSON del texto (puede venir con markdown)
            if "```json" in script_text:
                script_text = script_text.split("```json")[1].split("```")[0]
            elif "```" in script_text:
                script_text = script_text.split("```")[1].split("```")[0]
            
            script = json.loads(script_text.strip())
            
            print(f"✅ Guion generado ({len(script.get('scenes', []))} escenas)")
            return script
            
        except Exception as e:
            print(f"❌ Error al generar guion: {e}")
            print(f"Respuesta recibida: {script_text[:500]}")
            raise
    
    def process_video_analysis(self, analysis_path: str) -> Dict:
        """
        Procesa un análisis de video completo y genera narrativa + guion.
        
        Args:
            analysis_path: Ruta al archivo de análisis JSON
            
        Returns:
            Diccionario con narrativa y guion
        """
        print("="*80)
        print("📖 GENERACIÓN DE NARRATIVA: Mundo Toon Stickman")
        print("="*80)
        print()
        
        # Cargar análisis
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        transcript = analysis_data.get("transcript", {})
        people_count = len(analysis_data.get("people_detections", []))
        video_id = analysis_data.get("video_id", "unknown")
        
        print(f"📂 Video ID: {video_id}")
        print(f"👥 Personajes detectados: {people_count}")
        print()
        
        # Paso 1: Analizar contradicciones
        contradictions = self.analyze_contradictions(transcript)
        
        # Guardar análisis de contradicciones
        contradictions_path = self.narratives_dir / f"{video_id}_contradictions.txt"
        with open(contradictions_path, 'w', encoding='utf-8') as f:
            f.write(contradictions)
        
        print(f"💾 Contradicciones guardadas: {contradictions_path}")
        print()
        
        # Paso 2: Generar narrativa irónica
        narrative = self.generate_ironic_narrative(transcript, contradictions)
        
        # Guardar narrativa
        narrative_path = self.narratives_dir / f"{video_id}_narrative.txt"
        with open(narrative_path, 'w', encoding='utf-8') as f:
            f.write(narrative)
        
        print(f"💾 Narrativa guardada: {narrative_path}")
        print()
        
        # Paso 3: Generar guion de animación
        script = self.generate_animation_script(
            narrative,
            transcript,
            max(people_count // 10, 2)  # Agrupar personas en 2-3 personajes principales
        )
        
        # Guardar guion
        script_path = self.scripts_dir / f"{video_id}_script.json"
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Guion guardado: {script_path}")
        print()
        
        # Compilar resultados
        result = {
            "video_id": video_id,
            "contradictions": contradictions,
            "narrative": narrative,
            "script": script,
            "paths": {
                "contradictions": str(contradictions_path),
                "narrative": str(narrative_path),
                "script": str(script_path)
            }
        }
        
        print("="*80)
        print("✅ NARRATIVA Y GUION COMPLETADOS")
        print("="*80)
        print()
        
        return result


def main():
    """Función principal para pruebas."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 narrative_generator.py <ruta_al_analysis.json>")
        sys.exit(1)
    
    analysis_path = sys.argv[1]
    
    generator = NarrativeGenerator()
    result = generator.process_video_analysis(analysis_path)
    
    print(f"📊 Resumen:")
    print(f"   Escenas generadas: {len(result['script'].get('scenes', []))}")
    print(f"   Duración total: {result['script'].get('duration_seconds', 0)} segundos")


if __name__ == "__main__":
    main()
