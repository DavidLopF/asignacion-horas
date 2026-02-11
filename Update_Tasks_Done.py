from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from dotenv import load_dotenv
import ssl
import urllib3
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar variables de entorno para deshabilitar SSL completamente
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurar SSL globalmente para ignorar certificados autofirmados
ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de Azure DevOps
# El token se lee de la variable de entorno AZURE_DEVOPS_PAT
personal_access_token = os.environ.get('AZURE_DEVOPS_PAT', '')
if not personal_access_token:
    print("❌ Error: Variable de entorno AZURE_DEVOPS_PAT no configurada")
    print("   Ejecuta: export AZURE_DEVOPS_PAT='tu_token_aqui'")
    exit(1)
organization_url = 'https://periferiaitgrouptfs.visualstudio.com'
project_name = 'TERPEL'

# Configurar sesión con SSL deshabilitado
session = requests.Session()
session.verify = False

retry_strategy = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Autenticación
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

print("Configurando conexión a Azure DevOps...")

try:
    connection._client.session = session
    wit_client = connection.clients.get_work_item_tracking_client()
    print("✅ Cliente de Work Item Tracking creado exitosamente")
except Exception as e:
    print(f"❌ Error creando cliente: {e}")
    exit(1)

# Lista de IDs de tareas creadas que necesitan actualizarse a Done
task_ids = [
    1414633,  # 2026-01-01 - Bug 226620
    1414634,  # 2026-01-02 - Bug 226620
    1414635,  # 2026-01-03 - Bug 226620
    1414636,  # 2026-01-04 - Bug 226620
    1414637,  # 2026-01-05 - Bug 226620
    1414638,  # 2026-01-06 - Bug 226956
    1414639,  # 2026-01-07 - Bug 226956
    1414640,  # 2026-01-08 - Bug 226956
    1414641,  # 2026-01-09 - Bug 226956
    1414642,  # 2026-01-10 - Issue 227876
    1414643,  # 2026-01-13 - Issue 227876
    1414644,  # 2026-01-14 - Issue 227876
    1414645,  # 2026-01-15 - Issue 227876
    1414646,  # 2026-01-16 - Issue 227876
    1414647,  # 2026-01-17 - Issue 227876
    1414648,  # 2026-01-20 - Issue 227876
    1414649,  # 2026-01-21 - Issue 227876
    1414650,  # 2026-01-22 - Issue 227876
    1414651,  # 2026-01-23 - Issue 227876
    1414652,  # 2026-01-24 - Issue 227876
    1414653,  # 2026-01-27 - Issue 227876
    1414654,  # 2026-01-28 - Issue 227876
]

def update_task_to_done(task_id):
    """Actualiza el estado de una tarea a Done"""
    try:
        # Documento de actualización - cambiar estado a Done
        document = [
            {
                'op': 'add',
                'path': '/fields/System.State',
                'value': 'Done'
            }
        ]
        
        # Actualizar el work item
        updated_task = wit_client.update_work_item(
            document=document,
            id=task_id,
            project=project_name
        )
        
        print(f"✅ Tarea {task_id} actualizada a Done - Título: {updated_task.fields['System.Title']}")
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar tarea {task_id}: {e}")
        return False

# Ejecutar actualización de todas las tareas
print(f"\n🔄 Actualizando {len(task_ids)} tareas a estado 'Done'...\n")

success_count = 0
error_count = 0

for task_id in task_ids:
    if update_task_to_done(task_id):
        success_count += 1
    else:
        error_count += 1

print(f"\n📊 Resumen:")
print(f"   ✅ Tareas actualizadas correctamente: {success_count}")
print(f"   ❌ Tareas con error: {error_count}")
print(f"   📝 Total procesadas: {len(task_ids)}")
