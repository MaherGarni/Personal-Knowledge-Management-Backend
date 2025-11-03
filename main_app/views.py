from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Category, Lesson
from .serializers import CategorySerializer, LessonSerializer
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
            queryset = Category.objects.filter(hierarchy=1)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                updated_categories = Category.objects.filter(hierarchy=1)
                response_data = self.serializer_class(updated_categories, many=True)
                return Response(response_data.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print("line whatever,",serializer.errors)
            return Response({'eroor':str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CategoryDetail(APIView):
    serializer_class = CategorySerializer   
    lookup_field = 'id'
    
    def get(self, request, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            cat_lessons = Lesson.objects.all()
            serialized_lessons = LessonSerializer(cat_lessons, many=True)
            serializer = self.serializer_class(category)
            return Response({
                "category": serializer.data,
                "lessons": serialized_lessons.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    
    def put(self, request, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            serializer = self.serializer_class(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                queryset = Category.objects.filter(hierarchy=1)
                updated_categories = self.serializer_class(queryset, many=True).data
                return Response(updated_categories, status=status.HTTP_200_OK)
            print(serializer.errors, "line39")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            queryset = Category.objects.filter(hierarchy=1)
            updated_categories = self.serializer_class(queryset, many=True).data
            return Response(updated_categories, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class CategoryLessons(APIView):
    serializer_class = LessonSerializer
    def post(self, request, category_id):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                category = get_object_or_404(Category, id=category_id)
                category_serialized = CategorySerializer(category)
                queryset =  Lesson.objects.all()
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                "category": category_serialized.data,
                "lessons": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LessonDetail(APIView):
    serializer_class = LessonSerializer
    
    def put(self, request, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            serializer = self.serializer_class(lesson, data=request.data)
            if serializer.is_valid():
                serializer.save()
                queryset = Lesson.objects.all()
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                    "lessons":serializer.data,
                    "lesson": LessonSerializer(lesson).data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.delete()
            queryset = Lesson.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        