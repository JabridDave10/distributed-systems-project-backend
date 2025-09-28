import requests
import os
from typing import Dict, List, Any, Optional

class AssistantAIService:
    def __init__(self):
        self.openrouter_url = os.getenv("OPENROUTER_API_URL")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.openrouter_key:
            print("⚠️ OPENROUTER_API_KEY no está configurado - El servicio médico no funcionará")

    
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Realizar petición a OpenRouter API
        """
        if not self.openrouter_key:
            return {
                "error": "OPENROUTER_API_KEY no está configurado. Por favor, configura tu API key de OpenRouter."
            }
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "x-ai/grok-4-fast",
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        try:
            response = requests.post(self.openrouter_url, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                return {"error": "Respuesta inesperada de la API", "details": result}
            
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"]
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la petición: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}
    
    def consultar_enfermedad(self, enfermedad: str) -> Dict[str, Any]:
        """
        Consultar información detallada sobre una enfermedad
        """
        messages = [
            {
                "role": "system", 
                "content": """Eres un médico especialista con amplia experiencia. 
                Proporciona información médica precisa, clara y estructurada sobre enfermedades.
                Incluye: definición, síntomas principales, causas, factores de riesgo, 
                diagnóstico, tratamiento y prevención. Sé profesional pero accesible."""
            },
            {
                "role": "user", 
                "content": f"Proporciona información médica completa sobre: {enfermedad}"
            }
        ]
        
        return self._make_request(messages, max_tokens=1500)
    
    def diagnosticar_sintomas(self, sintomas: List[str], edad: Optional[int] = None, 
                            genero: Optional[str] = None) -> Dict[str, Any]:
        """
        Realizar diagnóstico basado en síntomas
        """
        sintomas_texto = ", ".join(sintomas)
        contexto_adicional = ""
        
        if edad:
            contexto_adicional += f" Edad: {edad} años."
        if genero:
            contexto_adicional += f" Género: {genero}."
        
        messages = [
            {
                "role": "system",
                "content": """Eres un médico especialista en diagnóstico diferencial. 
                Analiza los síntomas presentados y proporciona:
                1. Posibles diagnósticos (ordenados por probabilidad)
                2. Síntomas adicionales a evaluar
                3. Pruebas médicas recomendadas
                4. Urgencia del caso
                5. Recomendaciones inmediatas
                
                IMPORTANTE: Esto es solo para orientación médica. 
                Siempre recomienda consultar con un médico profesional."""
            },
            {
                "role": "user",
                "content": f"Síntomas presentados: {sintomas_texto}.{contexto_adicional}"
            }
        ]
        
        return self._make_request(messages, max_tokens=2000)
    
    def obtener_tratamiento(self, enfermedad: str, severidad: str = "moderada") -> Dict[str, Any]:
        """
        Obtener información sobre tratamientos para una enfermedad
        """
        messages = [
            {
                "role": "system",
                "content": """Eres un médico especialista en tratamientos médicos.
                Proporciona información detallada sobre tratamientos incluyendo:
                1. Tratamientos farmacológicos
                2. Tratamientos no farmacológicos
                3. Cambios en el estilo de vida
                4. Tiempo de recuperación esperado
                5. Posibles efectos secundarios
                6. Cuándo buscar atención médica urgente
                
                IMPORTANTE: Esta información es solo educativa. 
                Siempre recomienda consultar con un médico antes de iniciar cualquier tratamiento."""
            },
            {
                "role": "user",
                "content": f"Proporciona información sobre tratamientos para {enfermedad} con severidad {severidad}"
            }
        ]
        
        return self._make_request(messages, max_tokens=1500)
    
    def analizar_medicamento(self, medicamento: str) -> Dict[str, Any]:
        """
        Analizar información sobre un medicamento
        """
        messages = [
            {
                "role": "system",
                "content": """Eres un farmacéutico clínico especializado.
                Proporciona información detallada sobre medicamentos incluyendo:
                1. Indicaciones terapéuticas
                2. Dosis recomendadas
                3. Contraindicaciones
                4. Efectos secundarios
                5. Interacciones medicamentosas
                6. Precauciones especiales
                
                IMPORTANTE: Esta información es solo educativa.
                Siempre recomienda consultar con un médico o farmacéutico antes de usar cualquier medicamento."""
            },
            {
                "role": "user",
                "content": f"Proporciona información detallada sobre el medicamento: {medicamento}"
            }
        ]
        
        return self._make_request(messages, max_tokens=1500)
    
    def emergencia_medica(self, sintomas: List[str]) -> Dict[str, Any]:
        """
        Evaluar si los síntomas requieren atención médica urgente
        """
        sintomas_texto = ", ".join(sintomas)
        
        messages = [
            {
                "role": "system",
                "content": """Eres un médico de emergencias con experiencia en triaje.
                Evalúa la urgencia de los síntomas y proporciona:
                1. Nivel de urgencia (Baja/Media/Alta/Crítica)
                2. Tiempo recomendado para buscar atención
                3. Signos de alarma a vigilar
                4. Primeros auxilios si aplica
                5. Cuándo llamar a emergencias
                
                IMPORTANTE: En caso de síntomas graves, siempre recomienda buscar atención médica inmediata."""
            },
            {
                "role": "user",
                "content": f"Evalúa la urgencia de estos síntomas: {sintomas_texto}"
            }
        ]
        
        return self._make_request(messages, max_tokens=1000)
