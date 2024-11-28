import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

# llm_name = "gpt-3.5-turbo"
llm_name = "gpt-4o"
model = ChatOpenAI(
    api_key=openai_key,
    model=llm_name,
    temperature=0.5
    )


# from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase



# print(f"Database created successfully! {df}")

# Part 2: Prepare the sql prompt
MSSQL_AGENT_PREFIX = """

You are an agent designed to interact with a SQL database.
## Instructions:
- Given an input question, create a syntactically correct {dialect} query
to run, then look at the results of the query and return the answer.
- Unless the user specifies a specific number of examples they wish to
obtain, **ALWAYS** limit your query to at most {top_k} results.
- You can order the results by a relevant column to return the most
interesting examples in the database.
- Never query for all the columns from a specific table, only ask for
the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it.If you get an error
while executing a query,rewrite the query and try again.
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database.
- DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS
OF THE CALCULATIONS YOU HAVE DONE.
- Your response should be in Markdown. However, **when running  a SQL Query
in "Action Input", do not include the markdown backticks**.
Those are only for formatting the response, not for executing the command.
- ALWAYS, as part of your final answer, 
translate the answer into Spanish.
- For each sale obtained, perform a subsequent query to fetch detailed information related to that specific sale.

- If the question does not seem related to the database, just return
"I don\'t know" as the answer.
- Only use the below tools. Only use the information returned by the
below tools to construct your query and final answer.
- Do not make up table names, only use the tables returned by any of the
tools below.

## Tools:

"""

MSSQL_AGENT_FORMAT_INSTRUCTIONS = """

## Use the following format:

Question: la pregunta de entrada que debes responder.
Thought: siempre debes pensar qué hacer.
Action: la acción a realizar, debe ser una de [{tool_names}].
Action Input: la entrada para la acción.
Observation: el resultado de la acción.
... (este ciclo de Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: Ahora sé la respuesta final.
Final Answer: la respuesta final a la pregunta de entrada.

Ejemplo de Respuesta Final:
<=== Beginning of example

Question: ¿Cuál es la última venta, incluyendo sus detalles?

Thought: Para responder a esta pregunta, primero debo obtener el registro de la venta más reciente. Luego, consultaré los detalles de esa venta específica.

Action: query_sql_db
Action Input:
SELECT TOP 1 nv.id AS sale_id, nv.fecha AS sale_date, nv.total AS total_amount, nv.descuento AS discount
FROM nota_ventas nv
ORDER BY nv.fecha DESC;

Observation:
[{{"sale_id": 101, "sale_date": "2024-11-25", "total_amount": 150.00, "discount": 10.00}}]

Thought: Ahora sé cuál es la última venta. A continuación, necesito obtener los detalles de esta venta.

Action: query_sql_db
Action Input:
SELECT dv.producto_id AS product_id, p.nombre AS product_name, p.categoria AS category, dv.cantidad AS quantity, dv.precio AS unit_price
FROM detalle_venta dv
JOIN productos p ON dv.producto_id = p.id
WHERE dv.nota_venta_id = {{101}};

Observation:
[
  {{"product_id": 1, "product_name": "Cepillo Eléctrico", "quantity": 2, "unit_price": 50.00}},
  {{"product_id": 2, "product_name": "Irrigador Dental", "quantity": 1, "unit_price": 100.00}}
]

Thought: Ahora tengo los detalles de la última venta.

Final Answer: La última venta ocurrió el 25 de noviembre de 2024, con un total de $150.00 y un descuento de $10.00. Los detalles de la venta son los siguientes:
1. Producto: Cepillo Eléctrico, Cantidad: 2, Precio Unitario: $50.00
2. Producto: Irrigador Dental, Cantidad: 1, Precio Unitario: $100.00

===> End of Example

"""


# Explicación:
# Primero consulté la tabla `nota_ventas` para obtener la información de la venta más reciente, ordenada por la fecha de venta en orden descendente. Luego limité los resultados a 1 para obtener la última venta. Después, consulté la tabla `detalle_venta` y la uní con la tabla `productos` para buscar los detalles de la venta con ID 101, que era la última venta encontrada en la tabla `nota_ventas`. Esto incluyó los nombres, categorías, cantidades y precios unitarios de los productos involucrados.

# , also explain how you arrived at the answer.
# in a section beginning with: "Explanation:". Include the SQL query as
# part of the explanation section.
# - If the question does not seem related to the database, just return
# "I don\'t know" as the answer.
# - Only use the below tools. Only use the information returned by the
# below tools to construct your query and final answer.
# - Do not make up table names, only use the tables returned by any of the
# tools below.
# - as part of your final answer, please include the SQL query you used in json format or code format


db = SQLDatabase.from_uri(
        "postgresql://postgres:Lun8753azul@database-1.c562cwq2q9uo.us-east-2.rds.amazonaws.com:5432/cmmotors_nlp"
            #  "postgresql://postgres:rambo@localhost:5432/cmmotors_nlp"
        )

toolkit = SQLDatabaseToolkit(db=db, llm=model)

# QUESTION = """
#     Dame los detalles de la última venta con sus respectivos productos vendidos.
# """
sql_agent = create_sql_agent(
    prefix=MSSQL_AGENT_PREFIX,
    format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
    llm=model,
    toolkit=toolkit,
    top_k=30,
    verbose=True,
    agent_executor_kwargs={"handle_parsing_errors": True},
)

# res = sql_agent.invoke(QUESTION)

# print(res)


@csrf_exempt
@require_POST
def langhchain_get(request):
    mensaje = request.POST.get('mensaje')
    if mensaje is None:
        # mensaje = 'llego null'
        return JsonResponse({'error': 'el campo mensaje es requerido'}, status=400)
    result = sql_agent.invoke(mensaje)
    return JsonResponse(result, safe=False)


def hola(request):
    # realizar consutal sql, lista de usuarios
    # usuarios = db.query("SELECT * FROM users")
    # # print(usuarios);
    
    
    return JsonResponse({
        'mensaje': 'Hola mundo desde hola_chain q onda puto!!',
        # 'usuarios': usuarios   
    }, safe=False)


