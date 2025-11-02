from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Category
from .serializers import CategorySerializer
from django.shortcuts import get_object_or_404
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
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CategoryDetail(APIView):
    serializer_class = CategorySerializer   
    lookup_field = 'id'
    
    def put(self, request, category_id):
        print(request.data, "line32")
        try:
            category = get_object_or_404(Category, id=category_id)
            serializer = self.serializer_class(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                updated_categories = Category.objects.all()
                serializer = self.serializer_class(updated_categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.errors, "line39")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)