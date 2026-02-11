from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from datetime import datetime
import ssl
import urllib3
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configurar variables de entorno para deshabilitar SSL completamente
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurar SSL globalmente para ignorar certificados autofirmados
ssl._create_default_https_context = ssl._create_unverified_context

# Configurar SSL para ignorar certificados autofirmados
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Configuración SSL más agresiva
import ssl
import urllib3.util.ssl_

# Monkey patch para deshabilitar SSL completamente
def create_unverified_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

ssl._create_default_https_context = create_unverified_context

# Monkey patch adicional para urllib3
def ssl_wrap_socket(sock, keyfile=None, certfile=None, cert_reqs=None, ca_certs=None, server_side=False, ssl_version=None, ciphers=None, ssl_context=None, ca_cert_dir=None):
    return ssl.wrap_socket(sock, keyfile=keyfile, certfile=certfile, cert_reqs=ssl.CERT_NONE, ca_certs=ca_certs, server_side=server_side, ssl_version=ssl_version, ciphers=ciphers)

urllib3.util.ssl_.ssl_wrap_socket = ssl_wrap_socket

# Función para configurar SSL de manera más agresiva
def configure_ssl_unverified():
    """Configura SSL para ignorar completamente la verificación de certificados"""
    import ssl
    import urllib3
    
    # Deshabilitar verificación SSL en urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Configurar contexto SSL no verificado
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Aplicar configuración global
    ssl._create_default_https_context = ssl._create_unverified_context
    
    return ssl_context

# Aplicar configuración SSL
configure_ssl_unverified()

# Configuración de Azure DevOps
# El token se lee de la variable de entorno AZURE_DEVOPS_PAT
personal_access_token = os.environ.get('AZURE_DEVOPS_PAT', '')
if not personal_access_token:
    print("❌ Error: Variable de entorno AZURE_DEVOPS_PAT no configurada")
    print("   Ejecuta: export AZURE_DEVOPS_PAT='tu_token_aqui'")
    exit(1)
organization_url = 'https://periferiaitgrouptfs.visualstudio.com'
project_name = 'TERPEL'

# Configurar sesión con SSL completamente deshabilitado
session = requests.Session()
session.verify = False  # Deshabilitar verificación SSL

# Configurar retry strategy más agresiva
retry_strategy = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Configurar headers adicionales
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
})

# Configurar SSL completamente deshabilitado
session.cert = None

# Autenticación
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Configurar el cliente con SSL completamente deshabilitado
print("Configurando conexión a Azure DevOps...")
print("🔧 SSL completamente deshabilitado para entorno corporativo")

try:
    # Configurar la sesión personalizada
    connection._client.session = session
    print("✅ Sesión personalizada configurada")
    
    # Crear cliente de Work Item Tracking
    wit_client = connection.clients.get_work_item_tracking_client()
    print("✅ Cliente de Work Item Tracking creado exitosamente")
    
except Exception as e:
    print(f"❌ Error creando cliente: {e}")
    print("🔧 Intentando configuración alternativa...")
    
    try:
        # Configuración alternativa más agresiva
        import ssl
        
        # Crear contexto SSL completamente no verificado
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Configurar requests para usar este contexto
        session.verify = False
        session.cert = None
        
        # Recrear conexión
        connection = Connection(base_url=organization_url, creds=credentials)
        connection._client.session = session
        
        wit_client = connection.clients.get_work_item_tracking_client()
        print("✅ Cliente creado con configuración alternativa")
        
    except Exception as e2:
        print(f"❌ Error en configuración alternativa: {e2}")
        print("💡 El problema SSL persiste. Contacta al administrador de red.")
        exit(1)

# Función para crear una nueva tarea
def create_task(parent_id, title, date_input, description=None):
    try:

        parsed_date = datetime.strptime(date_input, "%Y-%m-%d")
        date = parsed_date.strftime("%Y-%m-%d")

        # Configurar fecha de inicio y fin con hora ajustada a las 07:00
        start_date = f"{date}T13:00:00Z"
        finish_date = f"{date}T23:00:00Z"  # Ambas fechas serán iguales
        print("Está es la fecha: " + date )
        
        # Usar descripción personalizada si está disponible, sino usar el título
        desc_value = description if description else title
        
        # Datos de la nueva tarea
        document = [
            {'op': 'add', 'path': '/fields/System.Title', 'value': title},
            {'op': 'add', 'path': '/fields/System.Description', 'value': desc_value},
            {'op': 'add', 'path': '/fields/System.State', 'value': 'To Do'},
            {'op': 'add', 'path': '/fields/System.WorkItemType', 'value': 'Task'},
            {'op': 'add', 'path': '/fields/System.AreaPath', 'value': 'TERPEL\\Terpel POS'},
            {'op': 'add', 'path': '/fields/System.IterationPath', 'value': 'TERPEL\\Terpel POS\\Sprint Octubre'},
            {'op': 'add', 'path': '/fields/Microsoft.VSTS.Scheduling.StartDate', 'value': start_date},
            {'op': 'add', 'path': '/fields/Microsoft.VSTS.Scheduling.FinishDate', 'value': finish_date},
            {'op': 'add', 'path': '/fields/Custom.a1add9b4-18a3-469d-aea2-57e9cc75dfaf', 'value': 9},
            {'op': 'add', 'path': '/fields/Custom.a217d865-bed7-43f6-979c-f16eb8a366eb', 'value': 9},
            {'op': 'add', 'path': '/fields/Custom.Apoyo', 'value': 'NO'},
            {'op': 'add', 'path': '/fields/ScrumPeriferia.Area', 'value': 'Desarrollo'},
            {'op': 'add', 'path': '/relations/-', 'value': {
                'rel': 'System.LinkTypes.Hierarchy-Reverse',
                'url': f'https://dev.azure.com/periferiaitgrouptfs/_apis/wit/workItems/{parent_id}'
            }}
        ]

        # Crear la tarea
        created_task = wit_client.create_work_item(document=document, project=project_name, type='Task')
        print(f"Tarea creada exitosamente: ID {created_task.id}, Título: {created_task.fields['System.Title']}")
    except Exception as e:
        print(f"Error al crear la tarea {title}: {e}")

# ID del PBI donde se asociarán las tareas
parent_pbi_id = 1411536

# Lista de tareas restantes a crear
# Días laborales de enero de 2026
tasks_to_create = [
    # Bug 226620 - Actualización del inventario de tanques - Dashboard (1-5 enero)
    {"title": "TS - 2026-01-01 - DLLF - 226620 - Bug 226620 - BUG | STG | HO | ACTUALIZACION DEL INVENTARIO DE TANQUES - DASHBOARD", "date": "2026-01-01", "description": "Fallo: No se actualiza correctamente el inventario de todos los tanques"},
    {"title": "TS - 2026-01-02 - DLLF - 226620 - BUG | STG | HO | ACTUALIZACION DEL INVENTARIO DE TANQUES - DASHBOARD", "date": "2026-01-02", "description": "Fallo: No se actualiza correctamente el inventario de todos los tanques"},
    {"title": "TS - 2026-01-03 - DLLF - 226620 - BUG | STG | HO | ACTUALIZACION DEL INVENTARIO DE TANQUES - DASHBOARD", "date": "2026-01-03", "description": "Fallo: No se actualiza correctamente el inventario de todos los tanques"},
    {"title": "TS - 2026-01-04 - DLLF - 226620 - BUG | STG | HO | ACTUALIZACION DEL INVENTARIO DE TANQUES - DASHBOARD", "date": "2026-01-04", "description": "Fallo: No se actualiza correctamente el inventario de todos los tanques"},
    {"title": "TS - 2026-01-05 - DLLF - 226620 - BUG | STG | HO | ACTUALIZACION DEL INVENTARIO DE TANQUES - DASHBOARD", "date": "2026-01-05", "description": "Fallo: No se actualiza correctamente el inventario de todos los tanques"},
    # Bug 226956 - Ventas RUMBO no descuenta lotes de combustible (6-9 enero)
    {"title": "TS - 2026-01-06 - DLLF - 226956 - Bug 226956 - BUG | HO - POS | ventas RUMBO", "date": "2026-01-06", "description": "FALLO: Al realizar ventas rumbo no descuenta la cantidad vendida en los lotes de combustible"},
    {"title": "TS - 2026-01-07 - DLLF - 226956 - BUG | HO - POS | ventas RUMBO", "date": "2026-01-07", "description": "FALLO: Al realizar ventas rumbo no descuenta la cantidad vendida en los lotes de combustible"},
    {"title": "TS - 2026-01-08 - DLLF - 226956 - BUG | HO - POS | ventas RUMBO", "date": "2026-01-08", "description": "FALLO: Al realizar ventas rumbo no descuenta la cantidad vendida en los lotes de combustible"},
    {"title": "TS - 2026-01-09 - DLLF - 226956 - BUG | HO - POS | ventas RUMBO", "date": "2026-01-09", "description": "FALLO: Al realizar ventas rumbo no descuenta la cantidad vendida en los lotes de combustible"},
    # Issue1 227876 - Optimización consulta balance operativo (10-28 enero)
    {"title": "TS - 2026-01-10 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-10"},
    {"title": "TS - 2026-01-13 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-13"},
    {"title": "TS - 2026-01-14 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-14"},
    {"title": "TS - 2026-01-15 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-15"},
    {"title": "TS - 2026-01-16 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-16"},
    {"title": "TS - 2026-01-17 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-17"},
    {"title": "TS - 2026-01-20 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-20"},
    {"title": "TS - 2026-01-21 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-21"},
    {"title": "TS - 2026-01-22 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-22"},
    {"title": "TS - 2026-01-23 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-23"},
    {"title": "TS - 2026-01-24 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-24"},
    {"title": "TS - 2026-01-27 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-27"},
    {"title": "TS - 2026-01-28 - DLLF - 227876 - Optimización consulta balance operativo", "date": "2026-01-28"}
]


#Crear las tareas ---> Descomentar para crear las tareas
for task in tasks_to_create:
    description = task.get("description")  # Obtener descripción si existe
    create_task(parent_pbi_id, task["title"], task["date"], description)

def get_status_options():
    try:
        print("\nObteniendo opciones del campo Status/State...")
        
        # Consulta directa que devuelve los valores únicos de State
        query = """
        SELECT [System.State] 
        FROM WorkItems 
        WHERE [System.WorkItemType] = 'Task' 
        GROUP BY [System.State]
        """
        
        query_results = wit_client.query_by_wiql({'query': query}, project_name)
        
        if query_results.work_items:
            print("\nValores de State encontrados en tareas existentes:")
            # Los valores ya están agrupados por la consulta WIQL
            for row in query_results.query_result_rows:
                print(f"- {row['System.State']}")
        else:
            print("No se encontraron tareas con valores de State definidos")
            
    except Exception as e:
        print(f"\nError al obtener opciones del campo Status: {e}")
        import traceback
        traceback.print_exc()


# Llamar a la función después de crear las tareas
get_status_options()        