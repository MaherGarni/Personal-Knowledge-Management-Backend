from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Category, Lesson
from .serializers import CategorySerializer, LessonSerializer, UserSerializer
from django.shortcuts import get_object_or_404
import os
from google import genai
from google.genai.types import GenerateContentConfig
import json
# import User model, UserSerializer, and RefreshToken...
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


client = genai.Client()

grading_rubric = {
    "1": "**Novice / Beginner** - Learner is just starting. Understands basic concepts but requires guidance to perform even simple tasks. Mistakes are frequent.",
    "2": "**Very Low Proficiency** - Learner can perform extremely simple tasks independently, but relies on examples or templates. Very limited problem-solving ability.",
    "3": "**Low Proficiency** - Learner can complete simple tasks with some confidence. Beginning to recognize patterns and make small adjustments without direct help.",
    "4": "**Basic / Elementary** - Learner performs basic tasks independently. Can follow instructions and replicate known patterns, but struggles with new or unexpected challenges.",
    "5": "**Moderate / Intermediate** - Learner handles common tasks reliably. Can apply knowledge to slightly unfamiliar situations. Mistakes are occasional and usually minor.",
    "6": "**Competent** - Learner demonstrates consistent understanding. Can troubleshoot standard problems and adapt existing knowledge to new contexts.",
    "7": "**Advanced** - Learner shows strong skill. Handles complex or multi-step tasks with minimal guidance. Begins to innovate or optimize processes.",
    "8": "**Highly Skilled / Expert** - Learner can manage complex challenges independently. Recognizes subtleties and nuances in the skill. Can guide or mentor others.",
    "9": "**Master** - Learner demonstrates deep understanding. Can tackle novel problems and create new approaches. Rarely makes mistakes.",        
    "10": "**Exceptional / Innovator** - Learner is capable of redefining or transforming the domain. Demonstrates creativity, foresight, and mastery beyond standard expectations.",
}


def gemini_AI(prompt):
    
    system_instruction = (
        """
        You are an intelligent learning-assistant AI that helps users organize knowledge and track skill development.

        Your responsibilities include:
        • Classifying lessons into the correct skill categories
        • Evaluating skill level based on the current lesson learned and parent / grandparent categories. The lesson and categories will be provided.
        • Assessing growth of lessons overtime when prompted to do so.

        Rules:
        • Always return JSON object in the specifid format.
        • If uncertainty occurs, choose the most logical and context-appropriate answer (not a creative one)
        """
    )

    
    
    config = GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
    )
    response = client.models.generate_content(
            model='gemini-2.5-flash-lite',  # Use a suitable model for the task
            contents=prompt,
            config=config
        )

    return json.loads(response.text[7:-4])
    
    
def lesson_category_check(lesson, category):
    prompt = f"""
                Determine if the lesson fits the selected category.
                Return JSON:
                {{
                  "belongs": true/false,
                }}

                Lesson:
                Title: "{lesson['title']}"
                Content: "{lesson['content']}"

                Selected Category: "{category.name}"
        """
    results = gemini_AI(prompt)
    return results

def update_skill_score(lesson, categories):
    prompt = f""" I am going to provide you with a scoring rubric that is used to judge all lessons being created within a 
            catgeory. Based on the lesson that the user has described having learned and the categories that the lesson is 
            related, judge the current lesson. Return a json object with the score: like this: {{ "score": number}}. Grading rubric: {grading_rubric}. Lesson to grade: {lesson} Lesson categories: {categories}"""
            
    results = gemini_AI(prompt)
    return results

def update_category_score(category, lessons):
    prompt = """
            I'm going to provide you with sets of lessons and thier scores, and based on the lessons i want to give a general 
    """

# User Registration
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            data = {
        	    'refresh': str(refresh),
        	    'access': str(refresh.access_token),
        	    'user': UserSerializer(user).data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Home(APIView):
    def get(self, request):
        content = Category.objects.annotate()
        print("sipfjworj")
        return Response({"categories":CategorySerializer(content, many=True).data})
    
class CategoriesIndex(APIView):
    serializer_class = CategorySerializer
    categories = Category.objects.all()
    categories3 = Category.objects.filter(hierarchy=3)
    # gemeni_ai(newCat="ui/ux" , categories=categories3)
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
            cat_lessons = Lesson.objects.filter(category=category_id)
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
        category = get_object_or_404(Category, id=category_id)
        # print(request.data, "jwebfiwubrfi")
        # 1 - check lesson contents matches user category choice

    
        lesson_categoy_results = lesson_category_check(request.data, category)
        print(lesson_categoy_results)
        
        if not lesson_categoy_results['belongs'] :
            return Response({"failed":"failed"})
        
        
        categories = {
    "grandparent-category": category.parent.parent.__str__(),
    "parent-category": category.parent.__str__(),
    "child-category_current": category.__str__()
}
        skill_results = update_skill_score(request.data, categories)
        
        data = request.data.copy()
        data["score"] = skill_results['score']
        
        try:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                category_serialized = CategorySerializer(category)
                queryset =  Lesson.objects.filter(category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                "category": category_serialized.data,
                "lessons": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LessonDetail(APIView):
    serializer_class = LessonSerializer
    
    def put(self, request, category_id, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            serializer = self.serializer_class(lesson, data=request.data)
            if serializer.is_valid():
                serializer.save()
                queryset = Lesson.objects.filter(category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                    "lessons":serializer.data,
                    "lesson": LessonSerializer(lesson).data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, category_id, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.delete()
            queryset = Lesson.objects.filter(category=category_id)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        