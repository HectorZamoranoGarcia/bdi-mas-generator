"""
tools.py — Herramientas (Tools) disponibles para los agentes del sistema BDI-MAS.

Incluye:
  • search_github_examples  — Consulta ejemplos oficiales de Jason en GitHub.
  • test_mas_code           — Compila/ejecuta un MAS en un directorio temporal.
  • save_mas_code           — Persiste el MAS final en disco (carpeta 'output').
  • exit_loop               — Señal de parada para el LoopAgent de refinamiento.
"""

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from google.adk.tools.tool_context import ToolContext

# Directorio de salida y estado global de reintentos

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 5
current_retries = 0
best_mas_state = {}
best_error_count = float("inf")


# Utilidad: localizar el binario de Jason

def resolve_jason_command():
    """
    Busca el ejecutable de Jason en este orden:
      1. Variable de entorno JASON_BIN
      2. Comando 'jason' disponible en el PATH
      3. Ruta típica de macOS  (/Applications/jason)
      4. Rutas típicas de Windows
    """
    env_path = os.getenv("JASON_BIN")
    if env_path:
        return env_path

    path_command = shutil.which("jason")
    if path_command:
        return path_command

    if Path("/Applications/jason").exists():
        return "/Applications/jason"

    for wp in [
        r"C:\Jason\bin\jason.bat",
        r"C:\Program Files\Jason\bin\jason.bat",
        r"C:\Program Files (x86)\Jason\bin\jason.bat",
    ]:
        if Path(wp).exists():
            return wp

    return None


# Búsqueda de ejemplos en GitHub

def search_github_examples(path: str = "") -> str:
    """
    Permite acceder a los ejemplos oficiales de código de Jason (BDI) en GitHub.
    Útil para consultar cómo se implementan ciertas características en Jason.

    Args:
        path: Ruta relativa del archivo/directorio de ejemplo a consultar
              dentro de la carpeta 'examples' de Jason.
              Déjalo vacío ("") para listar la raíz de ejemplos.
              Ejemplo: "auction/ag1.asl"
    """
    base_api_url = "https://api.github.com/repos/jason-lang/jason/contents/examples"
    url = f"{base_api_url}/{path}".strip("/")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Python-urllib"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

            if isinstance(data, list):
                items = [
                    f"[{item['type']}] {item['path'].replace('examples/', '', 1)}"
                    for item in data
                ]
                return (
                    f"Contenido de '{path or 'raíz'}':\n" + "\n".join(items)
                )

            elif isinstance(data, dict) and data.get("type") == "file":
                download_url = data.get("download_url")
                if download_url:
                    req_file = urllib.request.Request(
                        download_url, headers={"User-Agent": "Python-urllib"}
                    )
                    with urllib.request.urlopen(req_file) as f_res:
                        return f_res.read().decode("utf-8")
                return "Error: No se encontró la URL de descarga del archivo."
            else:
                return "Respuesta inesperada de la API de GitHub."

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"Error: No se encontró la ruta '{path}' en los ejemplos de Jason."
        if e.code == 403:
            return (
                "Error: Límite de peticiones a la API de GitHub excedido. "
                "Inténtalo más tarde."
            )
        return f"Error HTTP al acceder a GitHub: {e.code} - {e.reason}"
    except Exception as e:
        return f"Error al intentar acceder a los ejemplos: {e}"


# Compilar / ejecutar MAS en directorio temporal

def test_mas_code(mas2j_code: str, agents_dict: dict) -> str:
    """
    Guarda y ejecuta el código en un directorio temporal para probar el
    sistema Multi-Agente usando Jason.  NO guarda los archivos
    definitivamente, solo devuelve la salida para verificar si funciona.
    Límite de 5 intentos por sesión.

    Args:
        mas2j_code:  Contenido completo del archivo .mas2j.
        agents_dict: Diccionario {nombre_archivo.asl: contenido_asl}.
    """
    global current_retries, best_mas_state, best_error_count

    if current_retries >= MAX_RETRIES:
        return (
            f"ERROR: Has superado el límite de {MAX_RETRIES} intentos. "
            "Por favor, utiliza 'save_mas_code' para guardar el último "
            "código de inmediato y termina tu respuesta."
        )

    current_retries += 1

    temp_dir = Path("temp_mas_project")

    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Guardar .mas2j
        mas2j_file = temp_dir / "temp.mas2j"
        mas2j_file.write_text(mas2j_code, encoding="utf-8")

        # Guardar .asl
        for filename, content in agents_dict.items():
            if not filename.endswith(".asl"):
                filename += ".asl"
            (temp_dir / filename).write_text(content, encoding="utf-8")

        jason_command = resolve_jason_command()
        if not jason_command:
            return (
                "ERROR: No se ha encontrado Jason. Instálalo y define la "
                "variable de entorno JASON_BIN o añade 'jason' al PATH."
            )

        result = subprocess.run(
            [jason_command, "mas", "start", "--mas2j=temp.mas2j", "--console"],
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Heurística para contar errores
        error_count = 0
        if result.returncode != 0:
            error_count += 10
        if result.stderr:
            error_count += len(result.stderr.split("\n"))

        if error_count < best_error_count:
            best_error_count = error_count
            best_mas_state = {"mas2j": mas2j_code, "agents": agents_dict}

        output = (
            f"=== EJECUCIÓN DE PRUEBA (Intento {current_retries}/{MAX_RETRIES}) ===\n"
            f"Return code: {result.returncode}\n"
        )
        if result.stdout:
            output += f"--- STDOUT ---\n{result.stdout}\n"
        if result.stderr:
            output += f"--- STDERR ---\n{result.stderr}\n"

        return output

    except subprocess.TimeoutExpired as e:
        if best_error_count == float("inf"):
            best_mas_state = {"mas2j": mas2j_code, "agents": agents_dict}

        output = (
            f"=== EJECUCIÓN DE PRUEBA (Intento {current_retries}/{MAX_RETRIES}) ===\n"
            "AVISO: La ejecución alcanzó el tiempo límite (15 s). "
            "Esto es normal si Jason arranca una interfaz y no finaliza solo.\n"
        )
        if hasattr(e, "stdout") and e.stdout:
            stdout_str = (
                e.stdout.decode("utf-8") if isinstance(e.stdout, bytes) else e.stdout
            )
            output += f"--- STDOUT (parcial) ---\n{stdout_str}\n"
        return output

    except FileNotFoundError:
        return (
            "ERROR: El comando 'jason' no se encuentra en el sistema. "
            "Asegúrate de tener instalado Jason y agregado al PATH."
        )
    except Exception as e:
        return f"ERROR inesperado al ejecutar: {e}"
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


# Persistir MAS final en disco

def save_mas_code(
    mas_name: str, mas2j_code: str = "", agents_dict: dict = None
) -> str:
    """
    Guarda el sistema MAS completo (.mas2j + .asl) en su propia subcarpeta
    dentro de 'output/'.  Si se proporcionan mas2j_code y agents_dict
    los usa; en caso contrario recurre al mejor estado guardado durante
    las pruebas.

    Args:
        mas_name:    Nombre del proyecto (subcarpeta y archivo .mas2j).
        mas2j_code:  Contenido del .mas2j (opcional).
        agents_dict: Diccionario {nombre.asl: contenido} (opcional).
    """
    global current_retries, best_mas_state, best_error_count

    if agents_dict is None:
        agents_dict = {}

    project_dir = OUTPUT_DIR / mas_name
    project_dir.mkdir(parents=True, exist_ok=True)

    code_mas2j = mas2j_code if mas2j_code else best_mas_state.get("mas2j", "")
    code_agents = agents_dict if agents_dict else best_mas_state.get("agents", {})

    if not code_mas2j or not isinstance(code_agents, dict) or not code_agents:
        return "ERROR: No hay código generado para guardar o no se ha probado previamente."

    try:
        mas_filename = (
            f"{mas_name}.mas2j" if not mas_name.endswith(".mas2j") else mas_name
        )
        (project_dir / mas_filename).write_text(str(code_mas2j), encoding="utf-8")

        for filename, content in code_agents.items():
            if not filename.endswith(".asl"):
                filename += ".asl"
            (project_dir / filename).write_text(str(content), encoding="utf-8")

        # Reset para la próxima sesión
        current_retries = 0
        best_mas_state = {}
        best_error_count = float("inf")

        return f"ÉXITO: Proyecto BDI guardado correctamente en {project_dir}"
    except Exception as e:
        return f"ERROR inesperado al guardar: {e}"


# Señal de parada para LoopAgent

def exit_loop(tool_context: ToolContext):
    """
    Llama a esta función ÚNICAMENTE cuando el código generado es correcto
    y no necesita más correcciones, señalizando que el bucle iterativo
    de refinamiento debe finalizar.
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}
