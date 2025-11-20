#!/usr/bin/env python3
"""
Módulo de Generación de Escenas (Frames)
=========================================

Este módulo genera frames de animación 2D tipo stickman usando Pillow.
NO usa APIs de generación de imágenes, por lo que el costo es CERO.

Optimización de Costos:
- 100% código Python con Pillow (gratis)
- No requiere APIs de pago
- Ejecución local en Manus
"""

import os
import json
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class StickmanAnimator:
    """Animador de figuras stickman 2D."""
    
    def __init__(self, width=640, height=480, fps=10):
        """
        Inicializa el animador.
        
        Args:
            width (int): Ancho del frame en píxeles
            height (int): Alto del frame en píxeles
            fps (int): Frames por segundo
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.background_color = (255, 255, 255)  # Blanco
        self.stickman_color = (0, 0, 0)  # Negro
        self.line_width = 4
    
    def draw_stickman(self, draw, x, y, scale=1.0, pose="standing"):
        """
        Dibuja un stickman en una pose específica.
        
        Args:
            draw: Objeto ImageDraw de Pillow
            x (int): Posición X del centro del stickman
            y (int): Posición Y de la base del stickman
            scale (float): Escala del stickman
            pose (str): Pose del stickman
        """
        # Dimensiones base del stickman
        head_radius = int(20 * scale)
        body_length = int(60 * scale)
        arm_length = int(40 * scale)
        leg_length = int(50 * scale)
        
        # Cabeza
        head_y = y - body_length - leg_length - head_radius
        draw.ellipse(
            [x - head_radius, head_y - head_radius, 
             x + head_radius, head_y + head_radius],
            outline=self.stickman_color,
            width=self.line_width
        )
        
        # Cuerpo
        body_top = head_y + head_radius
        body_bottom = body_top + body_length
        draw.line(
            [x, body_top, x, body_bottom],
            fill=self.stickman_color,
            width=self.line_width
        )
        
        # Brazos y piernas según la pose
        if pose == "standing":
            self._draw_standing_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
        elif pose == "waving":
            self._draw_waving_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
        elif pose == "jumping":
            self._draw_jumping_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
        elif pose == "dancing":
            self._draw_dancing_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
        elif pose == "running":
            self._draw_running_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
        else:
            self._draw_standing_pose(draw, x, body_top, body_bottom, arm_length, leg_length, y)
    
    def _draw_standing_pose(self, draw, x, body_top, body_bottom, arm_length, leg_length, y):
        """Dibuja la pose de pie."""
        # Brazos hacia abajo
        draw.line([x, body_top + 10, x - arm_length, body_top + 40], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_top + 10, x + arm_length, body_top + 40], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Piernas rectas
        draw.line([x, body_bottom, x - 20, y], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_bottom, x + 20, y], 
                  fill=self.stickman_color, width=self.line_width)
    
    def _draw_waving_pose(self, draw, x, body_top, body_bottom, arm_length, leg_length, y):
        """Dibuja la pose saludando."""
        # Brazo izquierdo hacia abajo
        draw.line([x, body_top + 10, x - arm_length, body_top + 40], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Brazo derecho levantado (saludando)
        draw.line([x, body_top + 10, x + arm_length, body_top - 20], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Piernas rectas
        draw.line([x, body_bottom, x - 20, y], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_bottom, x + 20, y], 
                  fill=self.stickman_color, width=self.line_width)
    
    def _draw_jumping_pose(self, draw, x, body_top, body_bottom, arm_length, leg_length, y):
        """Dibuja la pose saltando."""
        # Brazos hacia arriba
        draw.line([x, body_top + 10, x - arm_length, body_top - 30], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_top + 10, x + arm_length, body_top - 30], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Piernas dobladas
        draw.line([x, body_bottom, x - 30, y - 20], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_bottom, x + 30, y - 20], 
                  fill=self.stickman_color, width=self.line_width)
    
    def _draw_dancing_pose(self, draw, x, body_top, body_bottom, arm_length, leg_length, y):
        """Dibuja la pose bailando."""
        # Brazos en ángulo
        draw.line([x, body_top + 10, x - arm_length + 10, body_top - 10], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_top + 10, x + arm_length - 10, body_top + 50], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Piernas en ángulo
        draw.line([x, body_bottom, x - 30, y], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_bottom, x + 15, y], 
                  fill=self.stickman_color, width=self.line_width)
    
    def _draw_running_pose(self, draw, x, body_top, body_bottom, arm_length, leg_length, y):
        """Dibuja la pose corriendo."""
        # Brazos en movimiento
        draw.line([x, body_top + 10, x - arm_length + 20, body_top - 10], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_top + 10, x + arm_length - 20, body_top + 50], 
                  fill=self.stickman_color, width=self.line_width)
        
        # Piernas en movimiento
        draw.line([x, body_bottom, x - 40, y], 
                  fill=self.stickman_color, width=self.line_width)
        draw.line([x, body_bottom, x + 25, y - 30], 
                  fill=self.stickman_color, width=self.line_width)
    
    def generate_scene_frames(self, scene_data, output_dir="output/frames"):
        """
        Genera frames para una escena específica.
        
        Args:
            scene_data (dict): Datos de la escena
            output_dir (str): Directorio de salida
            
        Returns:
            list: Lista de rutas a los frames generados
        """
        os.makedirs(output_dir, exist_ok=True)
        
        duration = scene_data.get('duration_seconds', 3)
        action = scene_data.get('action', 'standing')
        scene_num = scene_data.get('scene_number', 1)
        
        # Calcular número de frames
        num_frames = int(duration * self.fps)
        
        frames = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for frame_num in range(num_frames):
            # Crear imagen
            img = Image.new('RGB', (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Calcular posición y pose del stickman
            progress = frame_num / max(num_frames - 1, 1)
            
            if action == "waving":
                pose = "waving"
                x = self.width // 2
                y = self.height - 50
            elif action == "jumping":
                pose = "jumping"
                x = self.width // 2
                # Movimiento de salto (parábola)
                jump_height = 80
                y = self.height - 50 - int(jump_height * math.sin(progress * math.pi))
            elif action == "dancing":
                pose = "dancing"
                x = self.width // 2 + int(20 * math.sin(progress * math.pi * 4))
                y = self.height - 50
            elif action == "running":
                pose = "running"
                x = int(50 + progress * (self.width - 100))
                y = self.height - 50
            else:  # standing o default
                pose = "standing"
                x = self.width // 2
                y = self.height - 50
            
            # Dibujar stickman
            self.draw_stickman(draw, x, y, scale=1.0, pose=pose)
            
            # Añadir texto de la escena
            visual_desc = scene_data.get('visual_description', '')
            if visual_desc:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                # Dibujar texto en la parte superior
                draw.text((20, 20), visual_desc[:50], fill=(0, 0, 0), font=font)
            
            # Guardar frame
            filename = f"frame_{timestamp}_scene{scene_num}_{frame_num:04d}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            
            frames.append(filepath)
        
        print(f"✅ Generados {len(frames)} frames para escena {scene_num}")
        return frames
    
    def generate_frames_from_script(self, script_data, output_dir="output/frames"):
        """
        Genera todos los frames para un guion completo.
        
        Args:
            script_data (dict): Datos del guion
            output_dir (str): Directorio de salida
            
        Returns:
            list: Lista de todas las rutas a los frames generados
        """
        all_frames = []
        
        for scene in script_data.get('scenes', []):
            frames = self.generate_scene_frames(scene, output_dir)
            all_frames.extend(frames)
        
        return all_frames


def main():
    """Función de prueba del módulo."""
    import sys
    
    # Crear un guion de prueba
    test_script = {
        "title": "Stickman Divertido",
        "scenes": [
            {
                "scene_number": 1,
                "duration_seconds": 2,
                "visual_description": "Stickman saludando",
                "action": "waving"
            },
            {
                "scene_number": 2,
                "duration_seconds": 2,
                "visual_description": "Stickman saltando",
                "action": "jumping"
            },
            {
                "scene_number": 3,
                "duration_seconds": 2,
                "visual_description": "Stickman bailando",
                "action": "dancing"
            }
        ]
    }
    
    animator = StickmanAnimator(fps=10)
    frames = animator.generate_frames_from_script(test_script)
    
    print(f"\n🎨 Generados {len(frames)} frames en total")
    print(f"📁 Guardados en: output/frames/")


if __name__ == "__main__":
    main()
