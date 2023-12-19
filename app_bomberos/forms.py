from django import forms
from .models import AutoBombero, Mantencion , CustomUser, Compañia, Proveedor, TareaInterna, Insumo, DetInsumo, DetMant, Servicio
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput
from django.forms import formset_factory
 



class frmVehiculoBomberos(forms.ModelForm):
    class Meta:
        model = AutoBombero
        fields = '__all__'
        

class frmMantencion(forms.ModelForm):
    class Meta:
        model = Mantencion
        exclude = ['id_autobombero']
        widgets = {
            'fecha_mant': forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_prov'].label = 'Proveedor'
        self.fields['sueldo_a_m'].label = 'Sueldo actual del mecánico'
        self.fields['fecha_mant'].label = 'Fecha de mantención'
        self.fields['tareas_internas'].label = 'Tareas a realizar'
       

class frmMecanicoUser(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name','role', 'compania'] 
        


class frmLogin(AuthenticationForm):
    class Meta:
        model = CustomUser  # Reemplaza 'CustomUser' con el nombre de tu modelo de usuario personalizado
        fields = ['username', 'password'] 
        

class frmCompañia(forms.ModelForm):
    class Meta:
        model = Compañia
        fields = '__all__'
        
                
        
class frmProveedor(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_prov'].label = 'Clave proveedor' 
        
        
class frmModUser(UserChangeForm):
    class Meta:
        model=CustomUser
        fields=["username","first_name","last_name","email","role","compania","sueldo","valor_por_hora","admin"] 
        
class frmTareas(forms.ModelForm):
    class Meta:
        model = TareaInterna
        exclude = ['id_tarea']
        fields = '__all__'
        

class frmDetInsumo(forms.ModelForm):
    class Meta:
        model = DetInsumo
        exclude = ['id_mantencion']
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_insumo'].label = 'Nombre insumo'    
        

class frmInsumo(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = '__all__'
        
        # Personaliza las etiquetas de los campos de fecha
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_insumo'].label = 'Clave del insumo'
        self.fields['nomb_insumo'].label = 'Nombre del insumo'  
        

class frmDetMant(forms.ModelForm):
    class Meta:
        model = DetMant
        fields= '__all__'
        exclude = ['id_mantencion']
        
    cost_aplic = forms.DecimalField(widget=forms.TextInput(attrs={'readonly': 'readonly'})) 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cost_aplic'].label = 'Costo aplicado de la mantención'
        self.fields['h_h_aplic'].label = 'Horas hombre aplicadas'  


class frmServicio(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['costo_serv'].label = 'Costo del servicio'
        self.fields['descripcion'].label = 'Descripción' 
        self.fields['id_servicio'].label = 'Clave del servicio' 
    


