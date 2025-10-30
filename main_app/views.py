from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
from django.db.models import F
# Define the home view
class Home(APIView):
    def get(self, request):
        content = Category.objects.annotate()
        return Response({"categories":CategorySerializer(content, many=True).data})