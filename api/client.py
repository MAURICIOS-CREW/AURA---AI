import httpx
import os
import asyncio
from typing import Optional, Tuple
from .models import QRValidationRequest, QRValidationResponse, PlateValidationRequest, PlateValidationResponse

class AccessValidationClient:
    def __init__(self, host: Optional[str] = None):
        self.host = host or os.getenv("HOST", "http://localhost:8000")
        self.qr_endpoint = f"{self.host.rstrip('/')}/api/access/qr"
        
        plate_ep = os.getenv("PLATE_API_ENDPOINT", "/api/access/plate")
        if plate_ep.startswith("http"):
            self.plate_endpoint = plate_ep
        else:
            self.plate_endpoint = f"{self.host.rstrip('/')}/{plate_ep.lstrip('/')}"
        
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
                    self.qr_endpoint, 
                    json=request_data.model_dump(exclude_none=True),
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                # Log de la respuesta cruda para debugging
                print(f"[API DEBUG QR] Status Code: {response.status_code}")
                print(f"[API DEBUG QR] Raw Response Text: {response.text}")

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

    async def validate_plate(self, plate: str, device_id: Optional[str] = None) -> Tuple[bool, Optional[PlateValidationResponse]]:
        """
        Envía la placa leída por la IA a la API para validación de acceso.
        """
        device_identifier = device_id or os.getenv("DEVICE_IDENTIFIER", "CAM-Placas")
        request_data = PlateValidationRequest(
            plate=plate, 
            device_identifier=device_identifier
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.plate_endpoint, 
                    json=request_data.model_dump(exclude_none=True),
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                print(f"[API DEBUG PLACA] Status Code: {response.status_code}")
                print(f"[API DEBUG PLACA] Raw Response Text: {response.text}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        parsed_response = PlateValidationResponse(**data)
                        return True, parsed_response
                    except Exception:
                        # Si devuelve JSON plano u otra estructura de éxito 200
                        return True, PlateValidationResponse(status="success", message="Acceso concedido", data=None)
                else:
                    return False, None
        except httpx.RequestError as exc:
            print(f"[API ERROR] Excepción de red al validar placa {plate}: {exc}")
            return False, None
        except Exception as e:
            print(f"[API ERROR] Error validando placa '{plate}': {e}")
            return False, None

