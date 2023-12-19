from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone



# Create your models here.
class Compañia(models.Model):
    nombre_compania = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    # Agrega otros campos según tus necesidades

    def __str__(self):
        return self.nombre_compania


class AutoBombero(models.Model):
    clave = models.CharField(max_length=20,default="Desconocido")
    patente = models.CharField(max_length=20,default="Desconocido")
    tipo_vehiculo = models.CharField(max_length=50, default="Desconocido")
    marca = models.CharField(max_length=50, default="Desconocido")
    modelo = models.CharField(max_length=50)
    año = models.IntegerField(validators=[MinValueValidator(1900)], default=1900)
    nro_motor = models.CharField(max_length=100, default="Sin especificar")
    nro_chasis = models.CharField(max_length=150, default="Sin especificar")
    compania = models.ForeignKey(Compañia, on_delete=models.SET_NULL, null=True)
    imagen = models.ImageField(upload_to="imgprod", null=True)
    
    def __str__(self):
        return self.clave
   
    
class Mantencion(models.Model):
    ESTADO_CHOICES = [
        ('Preventiva', 'Preventiva'),
        ('Correctiva', 'Correctiva'),
        ('Externa', 'Externa'),
    ]
    
    id_autobombero = models.ForeignKey('AutoBombero', on_delete=models.CASCADE)
    fecha_mant = models.DateField(default=timezone.now)
    kilometraje = models.IntegerField(default=0)
    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_entrega = models.DateField(default=timezone.now)
    observaciones = models.TextField(default="", blank=True, null=True)
    tipo_mantencion = models.CharField(max_length=50, default="Preventiva", choices=ESTADO_CHOICES)
    sueldo_a_m = models.IntegerField(default=0, blank=True, null=True)
    id_prov = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, blank=True, null=True)
    tareas_internas = models.ManyToManyField('TareaInterna', blank=True, null=True)
    

    def __str__(self):
        return f'ID Mantenimiento #{self.id} - Clave: {self.id_autobombero.clave} - Patente: {self.id_autobombero.patente} - Compañia: {self.id_autobombero.compania}'



class Proveedor(models.Model):
    id_prov = models.IntegerField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=50, blank=True, null=True)
    # Agrega otros campos según tus necesidades

    def __str__(self):
        return f"{self.nombre_proveedor}"  
     
    
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('capitan', 'Capitán'),
        ('mecanico', 'Mecánico'),
        ('comandante', 'Comandante'),
    )
    
    # Agregar un campo de rol
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='mecanico')
    compania = models.ForeignKey(Compañia, on_delete=models.SET_NULL, default="Sin Compañia",null=True, blank=True)
    sueldo = models.IntegerField(default=0, blank=True, null=True)
    valor_por_hora = models.DecimalField(max_digits=9, decimal_places=2, default=0, blank=True, null=True)
    admin = models.BooleanField(default=False)
    

        
    
class TareaInterna(models.Model):
    id_tarea = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50, default="Sin descripción") 
    tipo_tarea = models.CharField(max_length=30, default="Sin tipo")
    
    def __str__(self):
        return f"{self.descripcion} - {self.tipo_tarea}"


class Insumo(models.Model):
    id_insumo = models.IntegerField(primary_key=True)
    nomb_insumo = models.CharField(max_length=50, default="Sin nombre")
    
    def __str__(self):
        return f"{self.nomb_insumo}"
    
    
class DetInsumo(models.Model):
    monto_insumo = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    cantidad_insumo = models.IntegerField(default=0)
    id_insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    id_mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE, related_name='detalles_insumo')
    
    def __str__(self):
        return f"{self.monto_insumo} - {self.cantidad_insumo} - {self.id_insumo} - {self.id_mantencion}"
 
    
    
class DetMant(models.Model):
    cost_aplic = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    h_h_aplic = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    id_mantencion = models.ForeignKey(Mantencion, on_delete=models.CASCADE, related_name='detalles_mantencion')
    id_servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, null=True, blank=True, related_name='detalles_servicio')
    
    def __str__(self):
        return f"{self.cost_aplic} - {self.h_h_aplic} - {self.id_mantencion}"
    
    
class Servicio(models.Model):
    id_servicio = models.IntegerField(primary_key=True)
    tipo_servicio = models.CharField(max_length=20, default="")
    descripcion = models.TextField(default="")
    costo_serv = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.tipo_servicio} - {self.descripcion} - {self.costo_serv}"
    
    
class RevisionDiaria(models.Model):
    id_rev_dia = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora_salida = models.CharField(max_length=10)
    hora_llegada = models.CharField(max_length=10)
    km_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    hora_motor = models.IntegerField()
    hora_bomba = models.IntegerField()
    est_carro = models.CharField(max_length=30)
    id_autobombero = models.ForeignKey(AutoBombero, null=True, blank=True, on_delete=models.CASCADE)
    id_user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    observaciones = models.CharField(max_length=2000, null=True, blank=True)
    
    def __str__(self):
        return f"{self.id_rev_dia} - {self.fecha} - {self.id_autobombero}"

    
    



    
    




