from rest_framework import viewsets
from .models import Selinux
from .serializers import SelinuxSerializer
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
class selinuxAPIview(viewsets.ModelViewSet):
    queryset = Selinux.objects.all()
    serializer_class = SelinuxSerializer
