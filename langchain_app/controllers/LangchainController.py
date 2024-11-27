"""
Controlador de la aplicación langchain
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent

from langchain.tools import BaseTool
import re

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

# try:
db = SQLDatabase.from_uri(
    "postgresql://postgres:rambo@localhost:5432/cmmotors_nlp"
    
)
#     print(db.table_info())
# except Exception as e:
#     print(f"Error al conectar a la base de datos: {e}")

# Configuración del modelo GPT
llm_gpt = ChatOpenAI(
    # model="gpt-3.5-turbo",
    model="gpt-4o",
    # api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    # max_tokens=100,
    )  # Cambia el modelo según tus necesidades

# llm_google = GoogleGenerativeAI(
#     # model="gemini-1.5-flash", 
#     model="gemini-1.5-pro",
#     # google_api_key=os.getenv("GOOGLE_API_KEY"),
#     )

class LimpiarSQLTool(BaseTool): 
    def __init__(self): 
        super().__init__(
            name="clear_sql",
            description="Cleans SQL queries by removing comments and unrelated text.") 
        
    def _run(self, sql): 
        return self.limpiar_sql(sql) 
        
    def clear_sql(self, sql): 
        # Eliminar comentarios de una sola línea 
        sql = re.sub(r'--.*', '', sql) 
        # Eliminar comentarios de múltiples líneas 
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL) 
        # Eliminar texto no relacionado con la consulta SQL, incluyendo la palabra clave 'sql' 
        sql = re.sub(r'[^a-zA-Z0-9_.,\s]', '', sql) 
        # Eliminar la palabra clave 'sql' 
        sql = re.sub(r'\bsql\b', '', sql, flags=re.IGNORECASE) 
        return sql.strip()

# 4. Inicializar el agente con la herramienta de limpieza
limpiador  = LimpiarSQLTool()


 
# Crear el toolkit para la base de datos
toolkit = SQLDatabaseToolkit(db=db, llm=llm_gpt)

# Crear el agente
agent_executor = create_sql_agent(
    llm=llm_gpt, 
    # db=db,  
    toolkit=toolkit,
    extra_tools=[limpiador],
    verbose=True,
    # early_stopping_method="generate",
    agent_type="tool-calling",
    prefix = """Try to relate the tables and return names, also do the queries with a limit of 2 more or less
        Example: 'select * from nota_ventas limit 2'
    """,
    # suuffix = "If no data is found after several attempts, respond with: 'No information found after several attempts.' ",
    # suffix = "final answer in Spanish {agent_scratchpad}",
    
    # early_stopping_method="generate",
    agent_executor_kwargs={"handle_parsing_errors": True},
    )

# Consulta en lenguaje natural
# query = "dame los detalles de la ultima venta registra, ignora responder con Id, accede a la tabla y busca el nombre o valores la que pertene la ID"
# response = agent_executor({
#     "input": query,  # Aquí se usa 'input' en lugar de 'messages'
# })


# print("Respuesta:", response)

def consulta(input_usuario):
    
    resultado = agent_executor({
            "input": input_usuario,
            "dialect": "PostgreSQL",
            "top_k": 10
           })
    return (resultado['output'])


# pregunta = 'Muéstrame los detalles de la última venta, incluyendo la información de los productos vendidos'

# print(consulta(pregunta))


@csrf_exempt
@require_POST
def langhchain_get(request):
    mensaje = request.POST.get('mensaje')
    if mensaje is None:
        # mensaje = 'llego null'
        return JsonResponse({'error': 'el campo mensaje es requerido'}, status=400)
    result = consulta(mensaje)
    return JsonResponse({'respuesta': result}, safe=False)

def hola(request):
    # realizar consutal sql, lista de usuarios
    # usuarios = db.query("SELECT * FROM users")
    # # print(usuarios);
    
    
    return JsonResponse({
        'mensaje': 'Hola mundo desde hola_chain q onda puto!!',
        # 'usuarios': usuarios   
    }, safe=False)

