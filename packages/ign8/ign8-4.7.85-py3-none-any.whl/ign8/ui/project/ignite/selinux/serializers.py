# selinux/serializers.py

from rest_framework import serializers
from .models import Selinux

class SelinuxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Selinux
        fields = '__all__'
