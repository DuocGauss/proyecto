from django.shortcuts import render, redirect, get_object_or_404
from .models import AutoBombero, Mantencion, Compañia, CustomUser,  Proveedor, TareaInterna, Servicio, DetMant, Insumo, RevisionDiaria
from .forms import frmVehiculoBomberos, frmMantencion, frmMecanicoUser, frmLogin, frmCompañia, frmProveedor, frmModUser, frmTareas, frmDetInsumo, frmInsumo, frmDetMant, frmServicio
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Subquery, OuterRef, F
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import formset_factory
from django.template.loader import render_to_string, get_template
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime
from django.db.models import Sum, Q
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
import io
from rest_framework import viewsets
from .serializers import srlzUser, srlzCarro, srlzRevision
#from .utils import obtener_lista_productos
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# ...


class UserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class=srlzUser
    
class AutoBomberoViewSet(viewsets.ModelViewSet):
    queryset = AutoBombero.objects.all()
    serializer_class = srlzCarro
    
class RevisionViewSet(viewsets.ModelViewSet):
    queryset = RevisionDiaria.objects.all()
    serializer_class = srlzRevision

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        # Incluye el campo 'role' en la respuesta
        response.data['role'] = user.role  # Asegúrate de que el modelo de usuario tenga un campo 'role'
        response.data['id'] = user.id
        response.data['compania'] = user.compania.nombre_compania if user.compania and user.compania.nombre_compania else "Sin compañía"

        return response

# Create your views here.
def index(request):
    obtener = AutoBombero.objects.all()
    
    # Obtén el último estado del carro para cada vehículo
    revisiones_ultimas = RevisionDiaria.objects.values('id_autobombero').annotate(
        last_revision=Max('id_rev_dia')
    ).values('id_autobombero', 'last_revision', 'est_carro')

    # Filtrar para obtener solo las revisiones más recientes
    revisiones_ultimas = RevisionDiaria.objects.filter(
        id_rev_dia__in=revisiones_ultimas.values('last_revision')
    )
    # Filtrar para obtener solo las revisiones del mismo vehículo
    revisiones_ultimas = revisiones_ultimas.filter(id_autobombero__in=obtener)
    print(revisiones_ultimas)
    #productos = obtener_lista_productos()
    user_role = request.session.get('user_role', None)
    
    usuario_autenticado = request.user

    # Verificar si el usuario es un capitán y tiene una compañía asignada
    if usuario_autenticado.is_authenticated and usuario_autenticado.role == 'capitan' and usuario_autenticado.compania:
        compañia_capitan = usuario_autenticado.compania

        # Filtrar los vehículos por la compañía del capitán actual
        obtener = AutoBombero.objects.filter(compania=compañia_capitan)
    else:
        # Si el usuario no es un capitán o no tiene una compañía asignada, mostrar todos los vehículos
        obtener = AutoBombero.objects.all()
    
    contexto = {
        'obtener': obtener,
        'user_role': user_role,
        'revisiones': revisiones_ultimas,
        #'productos': productos 
    }
    return render(request, 'app_bomberos/index.html', contexto)

@login_required
def gestion_vehiculos(request):
    obtener = AutoBombero.objects.all()
    
    query = request.GET.get('q')  # Obtener el término de búsqueda del request
    
    if query:
        # Filtrar mantenciones en función de la búsqueda
        obtener = obtener.filter(
            Q(clave__icontains=query) |
            Q(compania__nombre_compania__icontains=query) |
            Q(modelo__icontains=query) |
            Q(tipo_vehiculo__icontains=query) |
            Q(marca__icontains=query) |
            Q(año__icontains=query) |
            Q(patente__icontains=query) |
            Q(nro_motor__icontains=query) |
            Q(nro_chasis__icontains=query) 
        )
     # Agrega la paginación
    paginator = Paginator(obtener, 10)  # Divide los resultados en páginas, 10 registros por página
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    
    return render(request, 'app_bomberos/gestion_vehiculos.html', {
        'obtener': obtener
    })
    
@login_required
def add_vehiculo(request):
    form=frmVehiculoBomberos(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmVehiculoBomberos(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Vehículo Agregado!")

           return redirect(to="gestion_vehiculos")
        
    

    return render(request,"app_bomberos/add_vehiculo.html",contexto)


@login_required
def update_vehiculo(request,id):
    prod=get_object_or_404(AutoBombero,pk=id)
    form=frmVehiculoBomberos(instance=prod)
    #form.fields["id"].disabled=True
    contexto={
        "form":form
    }

    if request.method=="POST":
        form=frmVehiculoBomberos(data=request.POST,files=request.FILES,instance=prod)
        #form.fields["id"].disabled=False
        if form.is_valid():
            search=AutoBombero.objects.get(pk=prod.id)
            datos_form=form.cleaned_data
            search.clave=datos_form.get("clave")
            search.patente=datos_form.get("patente")
            search.tipo_vehiculo=datos_form.get("tipo_vehiculo")
            search.marca=datos_form.get("marca")
            search.modelo=datos_form.get("modelo")
            search.año=datos_form.get("año")
            search.nro_motor=datos_form.get("nro_motor")
            search.nro_chasis=datos_form.get("nro_chasis")
            search.compania=datos_form.get("compania")
            search.imagen=datos_form.get("imagen")
            search.save()
            messages.success(request,"Vehículo Modificado!")
            return redirect(to="gestion_vehiculos")
        contexto["form"]=form
        
    return render(request,"app_bomberos/update_vehiculo.html",contexto)

@login_required
def delete_vehiculo(request,id):
    v=get_object_or_404(AutoBombero,pk=id)
    contexto={
        "v":v
    }
    if request.method=="POST":
        v.delete()
        messages.success(request,"Vehículo Eliminado!")
        return redirect(to="gestion_vehiculos")

    return render(request,"app_bomberos/delete_vehiculo.html",contexto) 

@login_required
def detail_vehiculo(request, id):
    v = get_object_or_404(AutoBombero, pk=id)
    form_mantencion = frmMantencion(initial={'id_autobombero': v.id, 'sueldo_a_m': request.user.sueldo})
    user_role = request.session.get('user_role', None)

    if request.method == "POST":
        form_mantencion = frmMantencion(request.POST)
        if form_mantencion.is_valid():
            form_mantencion.save(commit=False)
            form_mantencion.instance.id_autobombero = v
            form_mantencion.instance.sueldo_a_m = request.user.sueldo
            form_mantencion.save()
            messages.success(request,"Mantención Agregada!")
            return redirect(to="index")

    contexto = {
        "v": v,
        "form_mantencion": form_mantencion,
        "user_role": user_role,
    }
    return render(request, "app_bomberos/detail_vehiculo.html", contexto)

@login_required
def gestion_tareas(request):
    obtener = TareaInterna.objects.all()
    user_role = request.session.get('user_role', None)
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_tarea__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo_tarea__icontains=query) 
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/gestion_tareas.html', contexto)
    
@login_required
def gestion_proveedor(request):
    obtener = Proveedor.objects.all()
    user_role = request.session.get('user_role', None)
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_prov__icontains=query) |
            Q(nombre_proveedor__icontains=query) 
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/gestion_proveedor.html', contexto)

@login_required
def gestion_insumo(request):
    obtener = Insumo.objects.all()
    user_role = request.session.get('user_role', None)
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_insumo__icontains=query) |
            Q(nomb_insumo__icontains=query) 
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/gestion_insumo.html', contexto)

@login_required
def gestion_servicios(request):
    obtener = Servicio.objects.all()
    user_role = request.session.get('user_role', None)
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_servicio__icontains=query) |
            Q(tipo_servicio__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(costo_serv__icontains=query) 
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/gestion_servicios.html', contexto)

@login_required
def delete_tarea(request,id):
    v=get_object_or_404(TareaInterna,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Tarea Eliminadas!")
        return redirect(to="gestion_tareas")
    
@login_required
def delete_proveedor(request,id):
    v=get_object_or_404(Proveedor,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Proveedor Eliminado!")
        return redirect(to="gestion_proveedor")
    
@login_required
def delete_insumo(request,id):
    v=get_object_or_404(Insumo,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Insumo Eliminado!")
        return redirect(to="gestion_insumo")
    
@login_required
def delete_servicio(request,id):
    v=get_object_or_404(Servicio,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Servicio Eliminado!")
        return redirect(to="gestion_servicios")


@login_required
def register_m(request):
    user_role = request.session.get('user_role', None)
    if request.method == 'POST':
        form = frmMecanicoUser(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            # Establecer la variable de sesión 'user_role' basada en el rol seleccionado
            user_role = form.cleaned_data.get('role')
            request.session['user_role'] = user_role
            
            # Asignar la compañía solo si el rol es "capitán"
            if user_role == 'capitan':
                compañia = form.cleaned_data.get('compañia')
                user.compañia = compañia
                user.save()
            messages.success(request,"Cuenta creada!")
            return redirect('index')  # Redirigir a la página de inicio después del registro
    else:
        form = frmMecanicoUser()
    
    contexto = {
        'form': form,
        'user_role': user_role,
    }
        
    return render(request, 'registration/register_m.html', contexto)



def login_custom(request):
    if request.method == 'POST':
        form = frmLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Establecer la variable de sesión 'user_role' basada en el rol del usuario
                if user.role:
                    request.session['user_role'] = user.role
                else:
                    # Si el usuario no tiene un rol definido, puedes manejarlo de alguna manera
                    pass
                
                return redirect('index')  # Redirigir a la página de inicio después de iniciar sesión
    else:
        form = frmLogin()
    
    return render(request, 'registration/login_custom.html', {'form': form})


@login_required
def logout_custom(request):
    logout(request)
    return redirect('index')  # Redirige a la página de inicio después de cerrar sesión

@login_required
def compañia(request):
    form=frmCompañia(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmCompañia(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Compañia Agregada!")

           return redirect(to="index")
       
    return render(request,"app_bomberos/compañia.html",contexto)


@login_required
def historial_mantenciones(request):
    obtener = Mantencion.objects.filter(tipo_mantencion = "Preventiva").order_by('fecha_ingreso')
    user_role = request.session.get('user_role', None)
    usuario_autenticado = request.user

    # Verificar si el usuario es un capitán y tiene una compañía asignada
    if usuario_autenticado.is_authenticated and usuario_autenticado.role == 'capitan' and usuario_autenticado.compania:
        compañia_capitan = usuario_autenticado.compania
        obtener = Mantencion.objects.filter(id_autobombero__compania=compañia_capitan, tipo_mantencion='Preventiva').order_by('fecha_ingreso')
    else:
        obtener = Mantencion.objects.filter(tipo_mantencion='Preventiva')
    
    query = request.GET.get('q')  # Obtener el término de búsqueda del request
    
    if query:
        # Filtrar mantenciones en función de la búsqueda
        obtener = obtener.filter(
            Q(id_autobombero__clave__icontains=query) |
            Q(id_autobombero__compania__nombre_compania__icontains=query) |
            Q(id_autobombero__modelo__icontains=query) |
            Q(id_autobombero__tipo_vehiculo__icontains=query) |
            Q(id_autobombero__marca__icontains=query) |
            Q(id_autobombero__año__icontains=query) |
            Q(id_autobombero__patente__icontains=query) |
            Q(id_autobombero__nro_motor__icontains=query) |
            Q(id_autobombero__nro_chasis__icontains=query) |
            Q(fecha_mant__icontains=query) |
            Q(tipo_mantencion__icontains=query) |
            Q(observaciones__icontains=query) |
            # Agrega más campos que deseas buscar
            Q(fecha_ingreso__icontains=query)  # Buscar por fecha de ingreso
        )
     # Agrega la paginación
    paginator = Paginator(obtener, 10)  # Divide los resultados en páginas, 10 registros por página
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/historial_mantenciones.html', contexto)

@login_required
def historial_correctiva(request):
    user_role = request.session.get('user_role', None)
    usuario_autenticado = request.user

    # Verificar si el usuario es un capitán y tiene una compañía asignada
    if usuario_autenticado.is_authenticated and usuario_autenticado.role == 'capitan' and usuario_autenticado.compania:
        compañia_capitan = usuario_autenticado.compania
        obtener = Mantencion.objects.filter(id_autobombero__compania=compañia_capitan, tipo_mantencion='Correctiva').order_by('fecha_ingreso')
    else:
        obtener = Mantencion.objects.filter(tipo_mantencion='Correctiva')
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_autobombero__clave__icontains=query) |
            Q(id_autobombero__compania__nombre_compania__icontains=query) |
            Q(id_autobombero__modelo__icontains=query) |
            Q(id_autobombero__tipo_vehiculo__icontains=query) |
            Q(id_autobombero__marca__icontains=query) |
            Q(id_autobombero__año__icontains=query) |
            Q(id_autobombero__patente__icontains=query) |
            Q(id_autobombero__nro_motor__icontains=query) |
            Q(id_autobombero__nro_chasis__icontains=query) |
            Q(fecha_mant__icontains=query) |
            Q(tipo_mantencion__icontains=query) |
            Q(observaciones__icontains=query) |
            # Agrega más campos que deseas buscar
            Q(fecha_ingreso__icontains=query)  # Buscar por fecha de ingreso
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/historial_correctiva.html', contexto)


@login_required
def historial_externo(request):
    user_role = request.session.get('user_role', None)
    usuario_autenticado = request.user

    # Verificar si el usuario es un capitán y tiene una compañía asignada
    if usuario_autenticado.is_authenticated and usuario_autenticado.role == 'capitan' and usuario_autenticado.compania:
        compañia_capitan = usuario_autenticado.compania
        obtener = Mantencion.objects.filter(id_autobombero__compania=compañia_capitan, tipo_mantencion = "Externa").order_by('fecha_ingreso')
    else:
        obtener = Mantencion.objects.filter(tipo_mantencion = "Externa").order_by('fecha_ingreso')
    
    query = request.GET.get('q')  
    
    if query:
        obtener = obtener.filter(
            Q(id_autobombero__clave__icontains=query) |
            Q(id_autobombero__compania__nombre_compania__icontains=query) |
            Q(id_autobombero__modelo__icontains=query) |
            Q(id_autobombero__tipo_vehiculo__icontains=query) |
            Q(id_autobombero__marca__icontains=query) |
            Q(id_autobombero__año__icontains=query) |
            Q(id_autobombero__patente__icontains=query) |
            Q(id_autobombero__nro_motor__icontains=query) |
            Q(id_autobombero__nro_chasis__icontains=query) |
            Q(fecha_mant__icontains=query) |
            Q(tipo_mantencion__icontains=query) |
            Q(observaciones__icontains=query) |
            # Agrega más campos que deseas buscar
            Q(fecha_ingreso__icontains=query)  # Buscar por fecha de ingreso
        )
    paginator = Paginator(obtener, 10)  
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/historial_externo.html', contexto)

@login_required
def generar_pdf(request, pk):
    # Obtén el registro de mantención preventiva específico por su clave primaria (pk)
    registro = get_object_or_404(Mantencion, pk=pk)
    tareas_internas = registro.tareas_internas.all()
    detalles_insumo = registro.detalles_insumo.all()
    detalles_mantencion = registro.detalles_mantencion.all()

    # Renderiza la plantilla HTML en un contexto con el registro y las tareas internas
    context = {'registro': registro, 'tareas_internas': tareas_internas, 'detalles_insumo': detalles_insumo, 'detalles_mantencion': detalles_mantencion}
    html = render_to_string('app_bomberos/generar_pdf.html', context)

    # Crea un objeto HttpResponse con tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mantencion_{registro.pk}.pdf"'

    # Crea el documento PDF con ReportLab
    p = canvas.Canvas(response)

    # Agrega el contenido HTML al documento PDF utilizando xhtml2pdf
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), pdf_file)

    # Agrega el PDF generado al objeto HttpResponse
    response.write(pdf_file.getvalue())

    return response

@login_required
def generar_pdf_externo(request, pk):
    registro = get_object_or_404(Mantencion, pk=pk)
    detalles_mantencion = registro.detalles_mantencion.all()
    context = {'registro': registro, 'detalles_mantencion': detalles_mantencion}
    html = render_to_string('app_bomberos/generar_pdf_externo.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mantencion_externo_{registro.pk}.pdf"'
    p = canvas.Canvas(response)
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), pdf_file)
    response.write(pdf_file.getvalue())
    return response

@login_required
def perfil_usuario(request):
    context = {}
    user_role = request.session.get('user_role', None)
    check = CustomUser.objects.filter(pk=request.user.id)
    if len(check)>0:
        data = CustomUser.objects.get(pk=request.user.id)
        context["data"] = data
    contexto = {
        'data': data,
        'user_role': user_role, 
    }
    return render(request,"app_bomberos/perfil_usuario.html",contexto)

@login_required
def detalle_mantencion(request, id):
    mantencion = Mantencion.objects.get(pk=id)
    user_role = request.session.get('user_role', None)
    # Obtiene el valor de valor_por_hora del usuario actual
    valor_por_hora = request.user.valor_por_hora

    if request.method == "POST":
        form = frmDetMant(data=request.POST, files=request.FILES)
        if form.is_valid():
            detalle_mantencion = form.save(commit=False)
            detalle_mantencion.id_mantencion = mantencion

            # Calcula el costo de la mantención automáticamente
            total_insumos = sum(det_insumo.monto_insumo * det_insumo.cantidad_insumo for det_insumo in mantencion.detalles_insumo.all())
            detalle_mantencion.cost_aplic = total_insumos


            # Calcula el costo total sumando las horas invertidas (si es válido)
            horas_hombres = form.cleaned_data.get('h_h_aplic')
            if horas_hombres:
                costo_total = detalle_mantencion.cost_aplic + (horas_hombres * valor_por_hora)
                detalle_mantencion.cost_aplic = costo_total

            detalle_mantencion.save()
            messages.success(request, "Detalles de mantención agregados!")
            return redirect("historial_mantenciones")
    else:
        total_insumos = sum(det_insumo.monto_insumo * det_insumo.cantidad_insumo for det_insumo in mantencion.detalles_insumo.all())
        costo_aplicado = total_insumos

        form = frmDetMant(initial={'id_mantencion': mantencion.id, 'cost_aplic': costo_aplicado})

    context = {
        "mantencion": mantencion,
        "form": form,
        "valor_por_hora": valor_por_hora,
        'user_role': user_role,
    }
    return render(request, "app_bomberos/detalle_mantencion.html", context)



@login_required
def estadisticas(request):
    user_role = request.session.get('user_role', None)
    chart_image = None

    if request.method == 'POST':
        fecha_range = request.POST.get('fechaRange')
        fecha_inicio, fecha_fin = fecha_range.split(' - ')
        
        detalles = Mantencion.objects.filter(fecha_mant__range=(fecha_inicio, fecha_fin))
    
        preventivos = detalles.filter(tipo_mantencion='Preventiva').count()
        correctivos = detalles.filter(tipo_mantencion='Correctiva').count()
        externos = detalles.filter(tipo_mantencion='Externa').count()
        
        d_preventivos = detalles.filter(tipo_mantencion='Preventiva')
        d_correctivos = detalles.filter(tipo_mantencion='Correctiva')
        d_externos = detalles.filter(tipo_mantencion='Externa')
        
        horas_invertidas_preventivos = d_preventivos.aggregate(total=Sum('detalles_mantencion__h_h_aplic'))['total'] or 0
        valor_gastado_preventivos = d_preventivos.aggregate(total_costo=Sum('detalles_mantencion__cost_aplic'))['total_costo'] or 0

        horas_invertidas_correctivos = d_correctivos.aggregate(total=Sum('detalles_mantencion__h_h_aplic'))['total'] or 0
        valor_gastado_correctivos = d_correctivos.aggregate(total_costo=Sum('detalles_mantencion__cost_aplic'))['total_costo'] or 0
        
        valor_gastado_externos = d_externos.aggregate(total_costo=Sum('detalles_mantencion__id_servicio__costo_serv'))['total_costo'] or 0
        
        horas_invertidas_total = horas_invertidas_preventivos + horas_invertidas_correctivos
        valor_gastado_total = valor_gastado_preventivos + valor_gastado_correctivos + valor_gastado_externos
        
        total_mantenimientos = detalles.count() 

        if total_mantenimientos > 0:
            porcentaje_preventivos = (preventivos / total_mantenimientos) * 100
            porcentaje_correctivos = (correctivos / total_mantenimientos) * 100
            porcentaje_externos = (externos / total_mantenimientos) * 100
            
            labels = 'M. Preventivo', 'M. Correctivo', 'M. Externo'
            sizes = [porcentaje_preventivos, porcentaje_correctivos, porcentaje_externos]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Guarda el gráfico en un archivo temporal
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            # Convierte la imagen del gráfico a una cadena base64
            chart_image = base64.b64encode(buffer.read()).decode('utf-8')
        else:
            # No hay registros, puedes mostrar un mensaje o manejarlo de acuerdo a tus necesidades
            buffer = BytesIO()
            buffer.write(b"No hay registros de mantenimiento para el rango de fechas seleccionado.")
            buffer.seek(0)
            porcentaje_correctivos = 0
            porcentaje_preventivos = 0
            porcentaje_externos = 0

    # Si se envió el campo 'generate_pdf' en el formulario, genera el PDF
    if 'generate_pdf' in request.POST:
        template_path = 'app_bomberos/generar_informe_pdf.html'
        context = {
            'horas_invertidas_total': horas_invertidas_total,
            'valor_gastado_total': valor_gastado_total,
            'horas_invertidas_preventivos': horas_invertidas_preventivos,
            'valor_gastado_preventivos': valor_gastado_preventivos,
            'horas_invertidas_correctivos': horas_invertidas_correctivos,
            'valor_gastado_correctivos': valor_gastado_correctivos,
            'valor_gastado_externos': valor_gastado_externos,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'chart_image': chart_image,
        }
        template = get_template(template_path)
        html = template.render(context)

        # Crear una respuesta HTTP con el tipo de contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

        # Crea el PDF a partir de la plantilla HTML
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Ha ocurrido un error al generar el PDF')
        
        return response

    contexto = {
        'user_role': user_role,
        'chart_image': chart_image,
    }
    
    return render(request, 'app_bomberos/estadisticas.html', contexto)

@login_required
def generar_informe_pdf(request, fecha_inicio, fecha_fin, horas_invertidas_total, valor_gastado_total,
                        horas_invertidas_preventivos,valor_gastado_preventivos,
                        horas_invertidas_correctivos,valor_gastado_correctivos,valor_gastado_externos,chart_image):
    template_path = 'app_bomberos/generar_informe_pdf.html'  # Reemplaza con la ruta a tu plantilla HTML
    context = {
        'horas_invertidas_total': horas_invertidas_total,
        'valor_gastado_total': valor_gastado_total,
        'horas_invertidas_preventivos': horas_invertidas_preventivos,
        'valor_gastado_preventivos': valor_gastado_preventivos,
        'horas_invertidas_correctivos': horas_invertidas_correctivos,
        'valor_gastado_correctivos': valor_gastado_correctivos,
        'valor_gastado_externos': valor_gastado_externos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'chart_image': chart_image,
    }
    template = get_template(template_path)
    html = template.render(context)

    # Crear una respuesta HTTP con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

    # Crea el PDF a partir de la plantilla HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Ha ocurrido un error al generar el PDF')
    
    return response


@login_required
def proveedor(request, id):
    form=frmProveedor(request.POST or None)
    user_role = request.session.get('user_role', None)
    contexto={
        "form":form,
        "user_role": user_role,
    }
    if request.method=="POST":
        form=frmProveedor(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Proveedor Agregado!")

           return redirect(to="detail_vehiculo" , id=id)
       
    return render(request,"app_bomberos/proveedor.html",contexto)

@login_required
def moduser(request,id):
    us = request.user
    user_role = request.session.get('user_role', None)
    form=frmModUser(instance=us)
    contexto={
        "form":form,
        "user_role": user_role,
    }

    if request.method=="POST":
        form=frmModUser(data=request.POST,files=request.FILES,instance=us)
        #form.fields["id"].disabled=False
        if form.is_valid():
            us_buscado=CustomUser.objects.get(id=us.id)
            datos_form=form.cleaned_data
            us_buscado.username=datos_form.get("username")
            us_buscado.first_name=datos_form.get("first_name")
            us_buscado.last_name=datos_form.get("last_name")
            us_buscado.email=datos_form.get("email")
            us_buscado.role=datos_form.get("role")
            us_buscado.compañia=datos_form.get("compañia")
            us_buscado.sueldo=datos_form.get("sueldo")
            us_buscado.valor_por_hora=datos_form.get("valor_por_hora")
            us_buscado.admin=datos_form.get("admin")
            us_buscado.save()
            messages.success(request,"Información Modificada!")
            return redirect(to="perfil_usuario")
        contexto["form"]=form
        
    return render(request,"app_bomberos/moduser.html",contexto) 

@login_required
def tarea_interna(request, id):
    form=frmTareas(request.POST or None)
    user_role = request.session.get('user_role', None)
    contexto={
        "form":form,
        "user_role": user_role,
    }
    if request.method=="POST":
        form=frmTareas(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Tareas Agregadas!")

           return redirect(to="detail_vehiculo" , id=id)
       
    return render(request,"app_bomberos/tarea_interna.html",contexto)


@login_required
def detalle_insumo(request, id):
    v = get_object_or_404(Mantencion, pk=id)
    form=frmDetInsumo(initial={'id_mantencion': v.id})
    user_role = request.session.get('user_role', None)
    contexto={
        "v":v,
        "form":form,
        "user_role": user_role,
    }
    if request.method=="POST":
        form=frmDetInsumo(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save(commit=False)
           form.instance.id_mantencion = v
           form.save()
           messages.success(request,"Insumos Agregados!")

           return redirect(to="historial_mantenciones" )
       
    return render(request,"app_bomberos/detalle_insumo.html",contexto)

@login_required    
def insumo(request, id):
    form=frmInsumo(request.POST or None)
    user_role = request.session.get('user_role', None)
    contexto={
        "form":form,
        "user_role": user_role,
    }
    if request.method=="POST":
        form=frmInsumo(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Datos Del Insumo Agregado!")

           return redirect("detalle_insumo", id=id)
       
    return render(request,"app_bomberos/insumo.html",contexto)


@login_required  
def servicio(request, id):
    form=frmServicio(request.POST or None)
    user_role = request.session.get('user_role', None)
    contexto={
        "form":form,
        "user_role": user_role,
    }
    if request.method=="POST":
        form=frmServicio(data=request.POST,files=request.FILES)
        if form.is_valid():
           form.save()
           messages.success(request,"Servicio Externo Agregado!")

           return redirect("detalle_mantencion", id=id)
       
    return render(request,"app_bomberos/servicio.html",contexto)



@login_required
def revision(request):
    obtener = RevisionDiaria.objects.all().order_by('-fecha')
    user_role = request.session.get('user_role', None)
    usuario_autenticado = request.user

    # Verificar si el usuario es un capitán y tiene una compañía asignada
    if usuario_autenticado.is_authenticated and usuario_autenticado.role == 'capitan' and usuario_autenticado.compania:
        compañia_capitan = usuario_autenticado.compania
        obtener = RevisionDiaria.objects.filter(id_autobombero__compania=compañia_capitan).order_by('-fecha')
    else:
        obtener = RevisionDiaria.objects.all().order_by('-fecha')
    
    query = request.GET.get('q')  # Obtener el término de búsqueda del request
    
    if query:
        # Filtrar mantenciones en función de la búsqueda
        obtener = obtener.filter(
            Q(id_autobombero__clave__icontains=query) |
            Q(id_autobombero__compania__nombre_compania__icontains=query) |
            Q(id_autobombero__modelo__icontains=query) |
            Q(id_autobombero__tipo_vehiculo__icontains=query) |
            Q(id_autobombero__marca__icontains=query) |
            Q(id_autobombero__año__icontains=query) |
            Q(id_autobombero__patente__icontains=query) |
            Q(id_autobombero__nro_motor__icontains=query) |
            Q(id_autobombero__nro_chasis__icontains=query) |
            Q(fecha__icontains=query) |
            Q(est_carro__icontains=query) |
            Q(observaciones__icontains=query) 
            # Agrega más campos que deseas buscar
        )
     # Agrega la paginación
    paginator = Paginator(obtener, 10)  # Divide los resultados en páginas, 10 registros por página
    page = request.GET.get('page')
    obtener = paginator.get_page(page)
    
    contexto = {
        'obtener': obtener,
        'user_role': user_role, 
    }
    return render(request, 'app_bomberos/revision.html', contexto)






