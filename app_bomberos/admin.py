from django.contrib import admin
from .models import AutoBombero, Mantencion, CustomUser, Compañia, Proveedor, TareaInterna, Insumo, DetInsumo, DetMant, Servicio, RevisionDiaria

# Register your models here.
admin.site.register(AutoBombero)
admin.site.register(Mantencion)
admin.site.register(CustomUser)
admin.site.register(Compañia)
admin.site.register(Proveedor)
admin.site.register(TareaInterna)
admin.site.register(Insumo)
admin.site.register(DetInsumo)
admin.site.register(DetMant)
admin.site.register(Servicio)
admin.site.register(RevisionDiaria)


