#!/usr/bin/env python3
"""
Módulo de Generación de Guiones con Gemini AI
==============================================

Este módulo utiliza la API de Google Gemini (gemini-2.5-flash) para generar
guiones estructurados para videos animados a partir de un prompt del usuario.

Optimización de Costos:
- Usa gemini-2.5-flash, el modelo más económico de Gemini
- Genera guiones concisos y estructurados
- Minimiza el número de tokens en la respuesta
"""

import os
import json
from datetime import datetime
from google import genai
from google.genai import types


class ScriptGenerator:
    """Generador de guiones de video con Gemini AI."""
    
    def __init__(self, api_key=None):
        """
        Inicializa el generador de guiones.
        
        Args:
            api_key (str): API key de Gemini. Si no se proporciona, se usa la variable de entorno.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere GEMINI_API_KEY")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"
    
    def generate_script(self, prompt, duration_seconds=10, style="stickman"):
        """
        Genera un guion estructurado para un video animado.
        
        Args:
            prompt (str): Descripción del video deseado
            duration_seconds (int): Duración aproximada del video en segundos
            style (str): Estilo de animación (stickman, cartoon, etc.)
            
        Returns:
            dict: Guion estructurado con escenas y diálogos
        """
        
        # Construir el prompt para Gemini
        system_prompt = f"""Eres un guionista experto en videos animados cortos y divertidos.
Tu tarea es crear un guion estructurado para un video de animación 2D tipo {style}.

El guion debe:
- Durar aproximadamente {duration_seconds} segundos
- Ser divertido y entretenido
- Tener entre 2-4 escenas
- Incluir diálogos cortos y descriptivos
- Describir las acciones visuales de forma clara

Formato de respuesta (JSON):
{{
  "title": "Título del video",
  "duration_seconds": {duration_seconds},
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 3,
      "visual_description": "Descripción de lo que se ve en pantalla",
      "dialogue": "Texto que se dice (si aplica)",
      "action": "Acción específica del personaje (ej: 'saluda con la mano', 'salta', 'corre')"
    }}
  ]
}}"""
        
        user_prompt = f"Crea un guion para: {prompt}"
        
        # Llamar a la API de Gemini
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=system_prompt),
                        types.Part(text=user_prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.9,  # Alta creatividad
                max_output_tokens=1000,  # Limitar para reducir costos
                response_mime_type="application/json"
            )
        )
        
        # Parsear la respuesta
        script_text = response.text
        
        try:
            script_data = json.loads(script_text)
        except json.JSONDecodeError:
            # Si Gemini no devuelve JSON válido, crear estructura básica
            script_data = {
                "title": prompt[:50],
                "duration_seconds": duration_seconds,
                "scenes": [
                    {
                        "scene_number": 1,
                        "duration_seconds": duration_seconds,
                        "visual_description": prompt,
                        "dialogue": "",
                        "action": "default"
                    }
                ]
            }
        
        # Añadir metadata
        script_data["generated_at"] = datetime.now().isoformat()
        script_data["style"] = style
        script_data["original_prompt"] = prompt
        
        return script_data
    
    def save_script(self, script_data, output_dir="output/scripts"):
        """
        Guarda el guion en un archivo JSON.
        
        Args:
            script_data (dict): Datos del guion
            output_dir (str): Directorio de salida
            
        Returns:
            str: Ruta del archivo guardado
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"script_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Guion guardado: {filepath}")
        return filepath


def main():
    """Función de prueba del módulo."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python script_generator.py '<prompt>'")
        print("Ejemplo: python script_generator.py 'Un stickman bailando feliz'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    generator = ScriptGenerator()
    script = generator.generate_script(prompt, duration_seconds=10, style="stickman")
    
    print("\n📝 Guion Generado:")
    print(json.dumps(script, ensure_ascii=False, indent=2))
    
    filepath = generator.save_script(script)
    print(f"\n💾 Guardado en: {filepath}")


if __name__ == "__main__":
    main()
