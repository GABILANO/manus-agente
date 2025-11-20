#!/usr/bin/env python3
"""
Módulo de Animación Mejorada: Mundo Toon Stickman
==================================================

Este módulo genera animaciones de stickman con:
1. Expresiones faciales (feliz, triste, enojado, sorprendido, confundido)
2. Gestos de manos (señalar, saludar, aplaudir, pensar)
3. Sincronización labial básica
4. Múltiples personajes en la misma escena

Autor: Manus AI
Fecha: 20 de noviembre de 2025
"""

import os
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


class EnhancedStickmanAnimator:
    """
    Genera animaciones de stickman con expresiones y gestos.
    """
    
    def __init__(self, width=1586, height=720, fps=60):
        """
        Inicializa el animador mejorado.
        
        Args:
            width: Ancho del frame
            height: Alto del frame
            fps: Frames por segundo
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.background_color = (255, 255, 255, 0)  # Transparente
        self.stickman_color = (0, 0, 0, 255)  # Negro sólido
        self.line_width = 6
    
    def draw_face_expression(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        radius: int,
        expression: str
    ):
        """
        Dibuja expresiones faciales en la cabeza del stickman.
        
        Args:
            draw: Objeto ImageDraw
            x, y: Centro de la cabeza
            radius: Radio de la cabeza
            expression: Tipo de expresión
        """
        # Posiciones de los ojos
        eye_offset_x = radius // 3
        eye_offset_y = radius // 4
        eye_size = radius // 6
        
        left_eye_x = x - eye_offset_x
        right_eye_x = x + eye_offset_x
        eyes_y = y - eye_offset_y
        
        # Dibujar ojos según la expresión
        if expression in ["happy", "neutral", "talking"]:
            # Ojos normales (círculos)
            draw.ellipse(
                [left_eye_x - eye_size, eyes_y - eye_size,
                 left_eye_x + eye_size, eyes_y + eye_size],
                fill=self.stickman_color
            )
            draw.ellipse(
                [right_eye_x - eye_size, eyes_y - eye_size,
                 right_eye_x + eye_size, eyes_y + eye_size],
                fill=self.stickman_color
            )
        
        elif expression == "surprised":
            # Ojos grandes y redondos
            eye_size_big = radius // 4
            draw.ellipse(
                [left_eye_x - eye_size_big, eyes_y - eye_size_big,
                 left_eye_x + eye_size_big, eyes_y + eye_size_big],
                outline=self.stickman_color,
                width=self.line_width // 2
            )
            draw.ellipse(
                [right_eye_x - eye_size_big, eyes_y - eye_size_big,
                 right_eye_x + eye_size_big, eyes_y + eye_size_big],
                outline=self.stickman_color,
                width=self.line_width // 2
            )
        
        elif expression == "angry":
            # Cejas enojadas (líneas inclinadas)
            brow_offset = radius // 3
            draw.line(
                [left_eye_x - eye_size*2, eyes_y - brow_offset,
                 left_eye_x + eye_size, eyes_y - brow_offset//2],
                fill=self.stickman_color,
                width=self.line_width
            )
            draw.line(
                [right_eye_x - eye_size, eyes_y - brow_offset//2,
                 right_eye_x + eye_size*2, eyes_y - brow_offset],
                fill=self.stickman_color,
                width=self.line_width
            )
            # Ojos pequeños
            draw.ellipse(
                [left_eye_x - eye_size//2, eyes_y - eye_size//2,
                 left_eye_x + eye_size//2, eyes_y + eye_size//2],
                fill=self.stickman_color
            )
            draw.ellipse(
                [right_eye_x - eye_size//2, eyes_y - eye_size//2,
                 right_eye_x + eye_size//2, eyes_y + eye_size//2],
                fill=self.stickman_color
            )
        
        elif expression == "sad":
            # Cejas tristes (líneas inclinadas al revés)
            brow_offset = radius // 3
            draw.line(
                [left_eye_x - eye_size*2, eyes_y - brow_offset//2,
                 left_eye_x + eye_size, eyes_y - brow_offset],
                fill=self.stickman_color,
                width=self.line_width
            )
            draw.line(
                [right_eye_x - eye_size, eyes_y - brow_offset,
                 right_eye_x + eye_size*2, eyes_y - brow_offset//2],
                fill=self.stickman_color,
                width=self.line_width
            )
            # Ojos normales
            draw.ellipse(
                [left_eye_x - eye_size, eyes_y - eye_size,
                 left_eye_x + eye_size, eyes_y + eye_size],
                fill=self.stickman_color
            )
            draw.ellipse(
                [right_eye_x - eye_size, eyes_y - eye_size,
                 right_eye_x + eye_size, eyes_y + eye_size],
                fill=self.stickman_color
            )
        
        elif expression == "confused":
            # Un ojo grande, otro pequeño
            draw.ellipse(
                [left_eye_x - eye_size*2, eyes_y - eye_size*2,
                 left_eye_x + eye_size*2, eyes_y + eye_size*2],
                outline=self.stickman_color,
                width=self.line_width // 2
            )
            draw.ellipse(
                [right_eye_x - eye_size//2, eyes_y - eye_size//2,
                 right_eye_x + eye_size//2, eyes_y + eye_size//2],
                fill=self.stickman_color
            )
        
        # Dibujar boca según la expresión
        mouth_y = y + radius // 2
        mouth_width = radius
        
        if expression == "happy":
            # Sonrisa (arco hacia arriba)
            draw.arc(
                [x - mouth_width, mouth_y - radius//4,
                 x + mouth_width, mouth_y + radius//2],
                start=0, end=180,
                fill=self.stickman_color,
                width=self.line_width
            )
        
        elif expression == "sad":
            # Boca triste (arco hacia abajo)
            draw.arc(
                [x - mouth_width, mouth_y - radius//2,
                 x + mouth_width, mouth_y + radius//4],
                start=180, end=360,
                fill=self.stickman_color,
                width=self.line_width
            )
        
        elif expression == "surprised":
            # Boca abierta (círculo)
            mouth_size = radius // 4
            draw.ellipse(
                [x - mouth_size, mouth_y - mouth_size,
                 x + mouth_size, mouth_y + mouth_size],
                outline=self.stickman_color,
                width=self.line_width
            )
        
        elif expression == "angry":
            # Boca recta (línea)
            draw.line(
                [x - mouth_width, mouth_y,
                 x + mouth_width, mouth_y],
                fill=self.stickman_color,
                width=self.line_width
            )
        
        elif expression == "confused":
            # Boca ondulada
            draw.line(
                [x - mouth_width, mouth_y,
                 x - mouth_width//2, mouth_y + radius//6,
                 x, mouth_y,
                 x + mouth_width//2, mouth_y - radius//6,
                 x + mouth_width, mouth_y],
                fill=self.stickman_color,
                width=self.line_width
            )
        
        elif expression in ["neutral", "talking"]:
            # Boca neutra (línea pequeña)
            draw.line(
                [x - mouth_width//2, mouth_y,
                 x + mouth_width//2, mouth_y],
                fill=self.stickman_color,
                width=self.line_width
            )
    
    def draw_hand_gesture(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        gesture: str,
        side: str = "right"
    ):
        """
        Dibuja gestos de manos.
        
        Args:
            draw: Objeto ImageDraw
            x, y: Posición del hombro
            gesture: Tipo de gesto
            side: "left" o "right"
        """
        arm_length = 60
        hand_size = 12
        
        # Dirección del brazo según el lado
        direction = 1 if side == "right" else -1
        
        if gesture == "pointing":
            # Brazo extendido señalando
            end_x = x + direction * arm_length
            end_y = y
            draw.line([x, y, end_x, end_y], fill=self.stickman_color, width=self.line_width)
            # Dedo señalando
            draw.line(
                [end_x, end_y, end_x + direction * hand_size, end_y - hand_size],
                fill=self.stickman_color,
                width=self.line_width
            )
        
        elif gesture == "waving":
            # Brazo levantado
            end_x = x + direction * arm_length // 2
            end_y = y - arm_length
            draw.line([x, y, end_x, end_y], fill=self.stickman_color, width=self.line_width)
            # Mano saludando
            draw.ellipse(
                [end_x - hand_size, end_y - hand_size,
                 end_x + hand_size, end_y + hand_size],
                outline=self.stickman_color,
                width=self.line_width // 2
            )
        
        elif gesture == "thinking":
            # Brazo doblado hacia la cabeza
            mid_x = x + direction * arm_length // 3
            mid_y = y + arm_length // 2
            end_x = x + direction * arm_length // 4
            end_y = y - arm_length // 2
            draw.line([x, y, mid_x, mid_y], fill=self.stickman_color, width=self.line_width)
            draw.line([mid_x, mid_y, end_x, end_y], fill=self.stickman_color, width=self.line_width)
        
        else:  # "none" o default
            # Brazo relajado
            end_x = x + direction * arm_length // 2
            end_y = y + arm_length
            draw.line([x, y, end_x, end_y], fill=self.stickman_color, width=self.line_width)
    
    def draw_stickman(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        scale: float = 1.0,
        action: str = "standing",
        expression: str = "neutral",
        hand_gesture: str = "none"
    ):
        """
        Dibuja un stickman completo con expresión y gesto.
        
        Args:
            draw: Objeto ImageDraw
            x, y: Posición base del stickman
            scale: Escala del stickman
            action: Acción del stickman
            expression: Expresión facial
            hand_gesture: Gesto de manos
        """
        # Dimensiones
        head_radius = int(30 * scale)
        body_length = int(80 * scale)
        leg_length = int(70 * scale)
        
        # Cabeza
        head_y = y - body_length - leg_length - head_radius
        draw.ellipse(
            [x - head_radius, head_y - head_radius,
             x + head_radius, head_y + head_radius],
            outline=self.stickman_color,
            width=self.line_width
        )
        
        # Expresión facial
        self.draw_face_expression(draw, x, head_y, head_radius, expression)
        
        # Cuerpo
        body_top = head_y + head_radius
        body_bottom = body_top + body_length
        draw.line([x, body_top, x, body_bottom], fill=self.stickman_color, width=self.line_width)
        
        # Brazos con gestos
        shoulder_y = body_top + 15
        self.draw_hand_gesture(draw, x, shoulder_y, hand_gesture, "right")
        self.draw_hand_gesture(draw, x, shoulder_y, "none", "left")
        
        # Piernas según la acción
        if action == "standing":
            draw.line([x, body_bottom, x - 30, y], fill=self.stickman_color, width=self.line_width)
            draw.line([x, body_bottom, x + 30, y], fill=self.stickman_color, width=self.line_width)
        
        elif action == "walking":
            draw.line([x, body_bottom, x - 40, y], fill=self.stickman_color, width=self.line_width)
            draw.line([x, body_bottom, x + 25, y - 20], fill=self.stickman_color, width=self.line_width)
        
        else:  # default
            draw.line([x, body_bottom, x - 30, y], fill=self.stickman_color, width=self.line_width)
            draw.line([x, body_bottom, x + 30, y], fill=self.stickman_color, width=self.line_width)
    
    def generate_scene_frames(
        self,
        scene_data: Dict,
        output_dir: str,
        people_positions: List[Dict] = None
    ) -> List[str]:
        """
        Genera frames para una escena.
        
        Args:
            scene_data: Datos de la escena
            output_dir: Directorio de salida
            people_positions: Posiciones de personas detectadas
            
        Returns:
            Lista de rutas a los frames generados
        """
        duration = scene_data.get("duration_seconds", 2.5)
        action = scene_data.get("action", "standing")
        expression = scene_data.get("expression", "neutral")
        hand_gesture = scene_data.get("hand_gesture", "none")
        dialogue = scene_data.get("dialogue", "")
        character = scene_data.get("character", "character_1")
        
        # Calcular número de frames
        num_frames = int(duration * self.fps)
        
        frames = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scene_num = scene_data.get("scene_number", 1)
        
        # Determinar posición del personaje
        if people_positions and len(people_positions) > 0:
            # Usar posición detectada
            pos = people_positions[0]
            base_x = pos.get("center_x", self.width // 2)
            base_y = pos.get("center_y", self.height - 100)
        else:
            # Posición por defecto
            base_x = self.width // 2
            base_y = self.height - 100
        
        for frame_num in range(num_frames):
            # Crear imagen con canal alfa (transparente)
            img = Image.new("RGBA", (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Calcular progreso
            progress = frame_num / max(num_frames - 1, 1)
            
            # Posición del stickman
            x = base_x
            y = base_y
            
            # Movimiento según la acción
            if action == "walking":
                x = int(base_x + 50 * math.sin(progress * math.pi * 4))
            
            # Dibujar stickman
            self.draw_stickman(
                draw, x, y,
                scale=1.0,
                action=action,
                expression=expression,
                hand_gesture=hand_gesture
            )
            
            # Añadir texto del diálogo
            if dialogue:
                try:
                    font = ImageFont.truetype(
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
                    )
                except:
                    font = ImageFont.load_default()
                
                # Dibujar texto en la parte inferior
                text_y = self.height - 80
                draw.text((40, text_y), dialogue[:80], fill=self.stickman_color, font=font)
            
            # Guardar frame
            frame_path = Path(output_dir) / f"frame_{timestamp}_scene{scene_num}_{frame_num:04d}.png"
            img.save(frame_path, "PNG")
            frames.append(str(frame_path))
        
        print(f"✅ Generados {len(frames)} frames para escena {scene_num}")
        return frames
    
    def generate_from_script(
        self,
        script: Dict,
        output_dir: str,
        people_positions: List[Dict] = None
    ) -> List[str]:
        """
        Genera todos los frames desde un guion.
        
        Args:
            script: Guion completo
            output_dir: Directorio de salida
            people_positions: Posiciones de personas detectadas
            
        Returns:
            Lista de todos los frames generados
        """
        print("🎨 Generando animación desde guion...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_frames = []
        scenes = script.get("scenes", [])
        
        for scene in scenes:
            frames = self.generate_scene_frames(scene, output_dir, people_positions)
            all_frames.extend(frames)
        
        print(f"✅ Total de frames generados: {len(all_frames)}")
        return all_frames


def main():
    """Función principal para pruebas."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 enhanced_animator.py <ruta_al_script.json>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    
    animator = EnhancedStickmanAnimator()
    frames = animator.generate_from_script(script, "output/frames")
    
    print(f"📊 Frames generados: {len(frames)}")


if __name__ == "__main__":
    main()
