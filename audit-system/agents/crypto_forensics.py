"""
Agente de Peritaje Forense y Cadena de Custodia Criptográfica
Responsable de sellar criptográficamente todas las evidencias
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from core.state import AgentState, AuditStatus


class CryptoForensicsAgent:
    """
    Agente que implementa la cadena de custodia criptográfica.
    Genera hashes SHA-256 de todos los artefactos y crea un manifiesto verificable.
    """
    
    def __init__(self, state: AgentState):
        self.state = state
    
    def execute(self) -> AgentState:
        """
        Ejecuta el sellado criptográfico de todas las evidencias.
        
        Returns:
            Estado actualizado con hashes y manifiesto
        """
        print("[CryptoForensics] Iniciando sellado criptográfico")
        
        self.state['status'] = AuditStatus.SEALING
        self.state['current_task'] = "Sellando evidencias con SHA-256"
        
        try:
            # Calcular hash de datos extraídos
            if self.state['extracted_data_path']:
                self.state['data_hash'] = self._calculate_file_hash(
                    self.state['extracted_data_path']
                )
                self._add_to_chain("extracted_data.csv", self.state['data_hash'])
            
            # Calcular hash de video
            if self.state['video_evidence_path']:
                self.state['video_hash'] = self._calculate_file_hash(
                    self.state['video_evidence_path']
                )
                self._add_to_chain("audit_session.webm", self.state['video_hash'])
            
            # Calcular hash de log (si existe)
            if self.state['log_path'] and os.path.exists(self.state['log_path']):
                self.state['log_hash'] = self._calculate_file_hash(
                    self.state['log_path']
                )
                self._add_to_chain("audit.log", self.state['log_hash'])
            
            # Calcular hashes de screenshots
            if self.state['screenshots_dir']:
                screenshot_hashes = self._hash_directory(self.state['screenshots_dir'])
                for filename, file_hash in screenshot_hashes.items():
                    self._add_to_chain(f"screenshots/{filename}", file_hash)
            
            # Generar manifiesto
            manifest_path = self._generate_manifest()
            self.state['manifest_path'] = manifest_path
            
            # Calcular hash del manifiesto (sello final)
            self.state['manifest_hash'] = self._calculate_file_hash(manifest_path)
            
            print(f"[CryptoForensics] Sellado completado. Hash del manifiesto: {self.state['manifest_hash'][:16]}...")
            
        except Exception as e:
            self.state['errors'].append(f"Error en CryptoForensics: {str(e)}")
            print(f"[CryptoForensics] ERROR: {e}")
        
        return self.state
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """
        Calcula el hash SHA-256 de un archivo.
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            Hash hexadecimal del archivo
        """
        sha256_hash = hashlib.sha256()
        
        with open(filepath, "rb") as f:
            # Leer en bloques para archivos grandes
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _hash_directory(self, directory: str) -> Dict[str, str]:
        """
        Calcula hashes de todos los archivos en un directorio.
        
        Args:
            directory: Ruta al directorio
            
        Returns:
            Diccionario {nombre_archivo: hash}
        """
        hashes = {}
        
        for filepath in Path(directory).rglob('*'):
            if filepath.is_file():
                relative_path = filepath.relative_to(directory)
                hashes[str(relative_path)] = self._calculate_file_hash(str(filepath))
        
        return hashes
    
    def _add_to_chain(self, filename: str, file_hash: str):
        """
        Añade un eslabón a la cadena de custodia.
        
        Args:
            filename: Nombre del archivo
            file_hash: Hash SHA-256 del archivo
        """
        chain_entry = {
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "sha256": file_hash,
            "previous_hash": self.state['chain_of_custody'][-1]['sha256'] if self.state['chain_of_custody'] else "GENESIS"
        }
        
        self.state['chain_of_custody'].append(chain_entry)
    
    def _generate_manifest(self) -> str:
        """
        Genera el manifiesto de la auditoría con todos los metadatos y hashes.
        
        Returns:
            Ruta al archivo manifest.json
        """
        manifest = {
            "audit_metadata": {
                "audit_id": self.state['audit_id'],
                "timestamp": self.state['timestamp'],
                "target_url": self.state['target_url'],
                "user_prompt": self.state['user_prompt'],
                "audit_depth": self.state['audit_depth'],
                "start_time": self.state['start_time'].isoformat() if self.state['start_time'] else None,
                "end_time": datetime.now().isoformat(),
                "total_records": self.state['total_records']
            },
            "evidence_hashes": {
                "extracted_data": self.state['data_hash'],
                "video_evidence": self.state['video_hash'],
                "audit_log": self.state['log_hash']
            },
            "chain_of_custody": self.state['chain_of_custody'],
            "verification": {
                "algorithm": "SHA-256",
                "created_by": "CryptoForensicsAgent v1.0",
                "verification_instructions": "Para verificar la integridad, recalcule el SHA-256 de cada archivo y compárelo con el hash en este manifiesto."
            }
        }
        
        manifest_path = os.path.join(self.state['output_dir'], 'manifest.json')
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"[CryptoForensics] Manifiesto generado: {manifest_path}")
        
        return manifest_path
    
    def verify_integrity(self, manifest_path: str) -> Dict[str, bool]:
        """
        Verifica la integridad de una auditoría usando su manifiesto.
        
        Args:
            manifest_path: Ruta al manifest.json
            
        Returns:
            Diccionario con resultados de verificación por archivo
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        verification_results = {}
        audit_dir = Path(manifest_path).parent
        
        for filename, expected_hash in manifest['evidence_hashes'].items():
            if expected_hash:
                filepath = audit_dir / filename
                if filepath.exists():
                    actual_hash = self._calculate_file_hash(str(filepath))
                    verification_results[filename] = (actual_hash == expected_hash)
                else:
                    verification_results[filename] = False
        
        return verification_results
