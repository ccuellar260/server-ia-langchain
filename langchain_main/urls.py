
from django.contrib import admin
from django.urls import path
from langchain_app.controllers import LangchainController
from langchain_app.controllers import LangchainAgentController

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', admin.site.urls),
    path('api/hola', LangchainAgentController.hola),
    path('api/consulta_ia', LangchainController.langhchain_get),
    path('api/consulta_ia_react', LangchainAgentController.langhchain_get),
]
