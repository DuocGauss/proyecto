from django.urls import path, include
from . import views
from .views import UserViewSet, AutoBomberoViewSet, CustomTokenObtainPairView, RevisionViewSet
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


router=routers.DefaultRouter()
router.register('customuser', UserViewSet)
router.register('autobombero', AutoBomberoViewSet)
router.register('revisiondiaria', views.RevisionViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path('gestion_vehiculos/',views.gestion_vehiculos,name="gestion_vehiculos"),
    path('add_vehiculo/',views.add_vehiculo,name="add_vehiculo"),
    path('update_vehiculo/<int:id>',views.update_vehiculo,name="update_vehiculo"),
    path('delete_vehiculo/<int:id>',views.delete_vehiculo,name="delete_vehiculo"),
    path('detail_vehiculo/<int:id>',views.detail_vehiculo,name="detail_vehiculo"),
    path('register_m/',views.register_m, name='register_m'),
    path('login_custom/', views.login_custom, name='login_custom'),
    path('logout_custom/', views.logout_custom, name='logout_custom'),
    path('compañia/',views.compañia,name="compañia"),
    path('historial_mantenciones/',views.historial_mantenciones,name="historial_mantenciones"),
    path('historial_correctiva/',views.historial_correctiva,name="historial_correctiva"),
    path('historial_externo/',views.historial_externo,name="historial_externo"),
    path('generar_pdf/<int:pk>/', views.generar_pdf, name='generar_pdf'),
    path('generar_pdf_externo/<int:pk>/', views.generar_pdf_externo, name='generar_pdf_externo'),
    path('perfil_usuario/', views.perfil_usuario, name='perfil_usuario'),
    path('detalle_mantencion/<int:id>/', views.detalle_mantencion, name='detalle_mantencion'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('generar_informe_pdf/', views.generar_informe_pdf, name='generar_informe_pdf'),
    path('proveedor/<int:id>',views.proveedor,name="proveedor"),
    path('moduser/<int:id>',views.moduser, name='moduser'),
    path('tarea_interna/<int:id>/', views.tarea_interna, name='tarea_interna'),
    path('gestion_tareas/',views.gestion_tareas,name="gestion_tareas"),
    path('gestion_proveedor/',views.gestion_proveedor,name="gestion_proveedor"),
    path('gestion_insumo/',views.gestion_insumo,name="gestion_insumo"),
    path('gestion_servicios/',views.gestion_servicios,name="gestion_servicios"),
    path('delete_tarea/<int:id>',views.delete_tarea,name="delete_tarea"),
    path('delete_proveedor/<int:id>',views.delete_proveedor,name="delete_proveedor"),
    path('delete_insumo/<int:id>',views.delete_insumo,name="delete_insumo"),
    path('delete_servicio/<int:id>',views.delete_servicio,name="delete_servicio"),
    path('detalle_insumo/<int:id>',views.detalle_insumo,name="detalle_insumo"),
    path('insumo/<int:id>',views.insumo,name="insumo"),
    path('servicio/<int:id>',views.servicio,name="servicio"),
    path('api/',include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('revision/',views.revision,name="revision"),
]
