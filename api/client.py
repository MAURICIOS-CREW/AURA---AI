import httpx
import os
import asyncio
from typing import Optional, Tuple
from .models import QRValidationRequest, QRValidationResponse

class AccessValidationClient:
    def __init__(self, host: Optional[str] = None):
        self.host = host or os.getenv("HOST", "http://localhost:8000")
        self.endpoint = f"{self.host.rstrip('/')}/api/access/qr"
        
    async def validate_qr(self, hash_code: str, device_id: Optional[str] = None) -> Tuple[bool, Optional[QRValidationResponse]]:
        """
        Envía el hash a la API y devuelve una tupla con (éxito_de_red, respuesta_parseada).
        No lanza excepciones para evitar bloquear los hilos asíncronos.
        """
        request_data = QRValidationRequest(
            hash=hash_code, 
            device_identifier=device_id
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint, 
                    json=request_data.model_dump(exclude_none=True),
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                # Log de la respuesta cruda para debugging
                print(f"[API DEBUG] Status Code: {response.status_code}")
                print(f"[API DEBUG] Raw Response Text: {response.text}")

                # Intentamos parsear a JSON independientemente del status code
                data = response.json()
                parsed_response = QRValidationResponse(**data)
                
                return True, parsed_response
        except httpx.RequestError as exc:
            print(f"[API ERROR] Excepción de red al solicitar {exc.request.url!r}.")
            return False, None
        except Exception as e:
            print(f"[API ERROR] Error validando QR '{hash_code}': {e}")
            return False, None
