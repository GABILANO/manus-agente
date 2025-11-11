"""
Agente Extractor y Videógrafo de Evidencias
Responsable de navegar sitios web, extraer datos y grabar video de la sesión
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import pandas as pd

from core.state import AgentState, AuditStatus


class EvidenceCollectorAgent:
    """
    Agente que combina extracción de datos con grabación de video forense.
    Implementa el protocolo de evidencia multimodal en tiempo real.
    """
    
    def __init__(self, state: AgentState):
        self.state = state
        self.browser: Browser = None
        self.page: Page = None
        
    async def execute(self) -> AgentState:
        """
        Ejecuta la fase de recolección de evidencias.
        
        Returns:
            Estado actualizado con datos extraídos y rutas a evidencias
        """
        print(f"[EvidenceCollector] Iniciando recolección para: {self.state['target_url']}")
        
        # Crear directorio de salida
        os.makedirs(self.state['output_dir'], exist_ok=True)
        screenshots_dir = os.path.join(self.state['output_dir'], 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        self.state['screenshots_dir'] = screenshots_dir
        self.state['status'] = AuditStatus.EXTRACTING
        self.state['current_task'] = "Extrayendo datos y grabando video"
        self.state['start_time'] = datetime.now()
        
        try:
            async with async_playwright() as p:
                # Configurar navegador con grabación de video
                self.browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                # Crear contexto con grabación de video habilitada
                video_dir = os.path.join(self.state['output_dir'], 'video_temp')
                context = await self.browser.new_context(
                    record_video_dir=video_dir,
                    record_video_size={"width": 1920, "height": 1080},
                    viewport={"width": 1920, "height": 1080}
                )
                
                self.page = await context.new_page()
                
                # Navegar a la URL objetivo
                print(f"[EvidenceCollector] Navegando a {self.state['target_url']}")
                await self.page.goto(self.state['target_url'], wait_until='networkidle')
                
                # Captura inicial
                await self._capture_screenshot("01_initial_load")
                
                # Extraer datos según el tipo de sitio
                extracted_data = await self._extract_data()
                
                # Guardar datos en CSV
                csv_path = os.path.join(self.state['output_dir'], 'extracted_data.csv')
                df = pd.DataFrame(extracted_data)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                self.state['extracted_data_path'] = csv_path
                self.state['extracted_records'] = extracted_data
                self.state['total_records'] = len(extracted_data)
                
                # Captura final
                await self._capture_screenshot("99_extraction_complete")
                
                # Cerrar contexto para finalizar video
                await context.close()
                
                # Mover video a ubicación final
                video_path = await self._finalize_video(video_dir)
                self.state['video_evidence_path'] = video_path
                
                await self.browser.close()
                
                print(f"[EvidenceCollector] Extracción completada: {len(extracted_data)} registros")
                
        except Exception as e:
            self.state['errors'].append(f"Error en EvidenceCollector: {str(e)}")
            self.state['status'] = AuditStatus.FAILED
            print(f"[EvidenceCollector] ERROR: {e}")
            
        return self.state
    
    async def _extract_data(self) -> List[Dict[str, Any]]:
        """
        Extrae datos estructurados de la página web.
        Detecta automáticamente el tipo de contenido y aplica la estrategia apropiada.
        """
        extracted_records = []
        
        # Obtener contenido HTML
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Estrategia 1: Buscar tablas HTML
        tables = soup.find_all('table')
        if tables:
            print(f"[EvidenceCollector] Encontradas {len(tables)} tablas")
            for idx, table in enumerate(tables):
                records = self._extract_table_data(table, idx)
                extracted_records.extend(records)
                await self._capture_screenshot(f"table_{idx}")
        
        # Estrategia 2: Buscar listas estructuradas
        lists = soup.find_all(['ul', 'ol'])
        if lists and not tables:
            print(f"[EvidenceCollector] Encontradas {len(lists)} listas")
            for idx, lst in enumerate(lists[:5]):  # Limitar a primeras 5
                records = self._extract_list_data(lst, idx)
                extracted_records.extend(records)
        
        # Estrategia 3: Extracción de metadatos generales
        if not extracted_records:
            print("[EvidenceCollector] Extrayendo metadatos generales")
            metadata = self._extract_page_metadata(soup)
            extracted_records.append(metadata)
        
        return extracted_records
    
    def _extract_table_data(self, table, table_idx: int) -> List[Dict[str, Any]]:
        """Extrae datos de una tabla HTML"""
        records = []
        
        # Buscar encabezados
        headers = []
        thead = table.find('thead')
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all(['th', 'td'])]
        else:
            # Intentar usar primera fila como encabezado
            first_row = table.find('tr')
            if first_row:
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
        
        # Si no hay encabezados, usar genéricos
        if not headers:
            headers = [f"Column_{i}" for i in range(10)]
        
        # Extraer filas
        tbody = table.find('tbody') or table
        rows = tbody.find_all('tr')[1 if not thead else 0:]
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) > 0:
                record = {
                    'table_id': table_idx,
                    'row_id': row_idx,
                    'timestamp_extracted': datetime.now().isoformat()
                }
                
                for idx, cell in enumerate(cells):
                    header = headers[idx] if idx < len(headers) else f"Column_{idx}"
                    record[header] = cell.get_text(strip=True)
                
                # Detectar si contiene datos sensibles
                record['contains_sensitive_keyword'] = self._detect_sensitive_keywords(record)
                
                records.append(record)
        
        return records
    
    def _extract_list_data(self, lst, list_idx: int) -> List[Dict[str, Any]]:
        """Extrae datos de listas HTML"""
        records = []
        items = lst.find_all('li')
        
        for idx, item in enumerate(items):
            record = {
                'list_id': list_idx,
                'item_id': idx,
                'content': item.get_text(strip=True),
                'timestamp_extracted': datetime.now().isoformat(),
                'contains_sensitive_keyword': self._detect_sensitive_keywords({'content': item.get_text()})
            }
            records.append(record)
        
        return records
    
    def _extract_page_metadata(self, soup) -> Dict[str, Any]:
        """Extrae metadatos generales de la página"""
        return {
            'title': soup.title.string if soup.title else 'Sin título',
            'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
            'h1_count': len(soup.find_all('h1')),
            'h2_count': len(soup.find_all('h2')),
            'link_count': len(soup.find_all('a')),
            'image_count': len(soup.find_all('img')),
            'timestamp_extracted': datetime.now().isoformat()
        }
    
    def _detect_sensitive_keywords(self, record: Dict[str, Any]) -> bool:
        """
        Detecta palabras clave que indican datos sensibles.
        Basado en el análisis de los documentos SCJN.
        """
        sensitive_keywords = [
            'datos sensibles', 'privado de libertad', 'materia penal',
            'confidencial', 'reservado', 'seguridad nacional',
            'datos personales', 'información clasificada'
        ]
        
        text = ' '.join(str(v).lower() for v in record.values())
        return any(keyword in text for keyword in sensitive_keywords)
    
    async def _capture_screenshot(self, name: str):
        """Captura una screenshot con timestamp"""
        if self.page:
            path = os.path.join(self.state['screenshots_dir'], f"{name}_{datetime.now().strftime('%H%M%S')}.png")
            await self.page.screenshot(path=path, full_page=True)
            print(f"[EvidenceCollector] Screenshot guardada: {name}")
    
    async def _finalize_video(self, video_dir: str) -> str:
        """
        Mueve el video grabado a su ubicación final y lo renombra.
        """
        # Playwright guarda el video con un nombre temporal
        video_files = list(Path(video_dir).glob('*.webm'))
        
        if video_files:
            temp_video = video_files[0]
            final_video_path = os.path.join(self.state['output_dir'], 'audit_session.webm')
            temp_video.rename(final_video_path)
            
            # Limpiar directorio temporal
            os.rmdir(video_dir)
            
            print(f"[EvidenceCollector] Video guardado: {final_video_path}")
            return final_video_path
        
        return None
