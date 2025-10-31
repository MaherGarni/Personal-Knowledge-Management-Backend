from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Category
from .serializers import CategorySerializer
from django.db.models import F
# Define the home view
class Home(APIView):
    def get(self, request):
        content = Category.objects.annotate()
        return Response({"categories":CategorySerializer(content, many=True).data})
    
    
    
class CategoriesIndex(APIView):
    serializer_class = CategorySerializer
    categories = Category.objects.all()

    

    def get(self, request):
        try:
            queryset = Category.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            # print(serializer.errors)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)