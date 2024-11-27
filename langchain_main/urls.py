
from django.contrib import admin
from django.urls import path
from langchain_app.controllers import LangchainController

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', admin.site.urls),
    path('api/hola', LangchainController.hola),
    path('api/consulta_ia', LangchainController.langhchain_get),
    # path('api/consulta_ia_react', LangchainController.langhchain_get_react),
]
