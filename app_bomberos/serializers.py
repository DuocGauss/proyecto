from rest_framework import serializers
from .models import CustomUser, AutoBombero, Compañia, RevisionDiaria

class CompañiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compañia
        fields = ["nombre_compania", "direccion"] 

class srlzUser(serializers.ModelSerializer):
    compania = CompañiaSerializer()
    class Meta:
        model=CustomUser
        fields=["id","username","password","first_name","last_name","email","role","compania","sueldo","valor_por_hora","admin"]               

class srlzCarro(serializers.ModelSerializer):
    compania = CompañiaSerializer()
    class Meta:
        model = AutoBombero
        fields = ["id","clave", "patente", "tipo_vehiculo", "marca", "modelo", "año", "nro_motor", "nro_chasis", "compania", "imagen"]
        
        
class srlzRevision(serializers.ModelSerializer):
    class Meta:
        model = RevisionDiaria
        fields = ["id_rev_dia", "fecha", "hora_salida", "hora_llegada", "km_entrada", "hora_motor", "hora_bomba", "est_carro", "id_autobombero","id_user","observaciones"]