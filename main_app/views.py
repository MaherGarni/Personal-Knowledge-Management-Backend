from unicodedata import category

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
# new import!
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny



client = genai.Client()

grading_rubric = {
    "1-10":   "**Novice / Beginner** - Learner is just starting. Understands basic concepts but requires guidance to perform even simple tasks. Mistakes are frequent.",
    "11-20":  "**Very Low Proficiency** - Learner can perform extremely simple tasks independently, but relies on examples or templates. Very limited problem-solving ability.",
    "21-30":  "**Low Proficiency** - Learner can complete simple tasks with some confidence. Beginning to recognize patterns and make small adjustments without direct help.",
    "31-40":  "**Basic / Elementary** - Learner performs basic tasks independently. Can follow instructions and replicate known patterns, but struggles with new or unexpected challenges.",
    "41-50":  "**Moderate / Intermediate** - Learner handles common tasks reliably. Can apply knowledge to slightly unfamiliar situations. Mistakes are occasional and usually minor.",
    "51-60":  "**Competent** - Learner demonstrates consistent understanding. Can troubleshoot standard problems and adapt existing knowledge to new contexts.",
    "61-70":  "**Advanced** - Learner shows strong skill. Handles complex or multi-step tasks with minimal guidance. Begins to innovate or optimize processes.",
    "71-80":  "**Highly Skilled / Expert** - Learner can manage complex challenges independently. Recognizes subtleties and nuances in the skill. Can guide or mentor others.",
    "81-90":  "**Master** - Learner demonstrates deep understanding. Can tackle novel problems and create new approaches. Rarely makes mistakes.",
    "91-100": "**Exceptional / Innovator** - Learner is capable of redefining or transforming the domain. Demonstrates creativity, foresight, and mastery beyond standard expectations.",
}

advancement_rubric = {
    "1-10":   "**Foundational** - Core definitions, basic terminology, and introductory concepts. No prior knowledge required to understand the topic.",
    "11-20":  "**Basic** - Simple, well-documented concepts with clear steps. Requires little to no background knowledge.",
    "21-30":  "**Elementary** - Slightly more involved but still straightforward. Requires understanding of foundational concepts first.",
    "31-40":  "**Lower Intermediate** - Topics that require combining multiple basic concepts. Some ambiguity in how to approach them.",
    "41-50":  "**Intermediate** - Requires solid foundational knowledge. Multiple valid approaches exist and context starts to matter.",
    "51-60":  "**Upper Intermediate** - Nuanced topics where tradeoffs and context significantly affect the right approach.",
    "61-70":  "**Advanced** - Complex topics requiring deep understanding of underlying principles, not just surface knowledge.",
    "71-80":  "**Highly Advanced** - Topics that combine multiple domains or require significant experience to reason about correctly.",
    "81-90":  "**Expert-Level** - Highly specialized topics requiring synthesis of knowledge across multiple areas. Few clear resources exist.",
    "91-100": "**Pioneering** - Research-level or domain-redefining topics. Requires mastery of the entire field to engage with meaningfully.",
}

def gemini_AI(prompt):
    
    system_instruction = (
        """
        You are an intelligent learning-assistant AI that helps users organize knowledge and track skill development.

        Your responsibilities include:
        • Classifying lessons into the correct skill categories
        • Scoring learner's lessons based on how well learner demonstareted understanding. plus how advance the topic is.  
        • Assessing growth of lessons overtime when prompted to do so.

        Rules:
        • Always return JSON object in the specifid format.
        • If uncertainty occurs, choose the most logical and context-appropriate answer (not a creative one)
        """
    )    

    config = GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        response_mime_type="application/json"
    )
    response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',  # Use a suitable model for the task
            contents=prompt,
            config=config
        )


    return json.loads(response.text)
    
    
def lesson_category_check(lesson, category):
    prompt = f"""
                Determine if the lesson fits the selected category. lesson don't have to match the category name exactly, 
                at least it could be considerd under that category.
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

def lesson_score(lesson, categories):
    prompt = f"""I'm providing you with a lesson and your job is to evaluate two things: 
                - how well learner demonstrated understanding of the lesson provided, considering the categories it falls under. 
                - How advance the topic is, based on the categories it falls under. 
                
                you'll be provided with the lesson's title and content, and the categories it belongs to (including the parent category and grandparent category).
                As well as the advancement rubric to evaluate the advancement level of the topic of the lesson.
                
                lesson's info :
                title : {lesson['title']}
                content : {lesson['content']}
                
                lesson's categories : {categories}
                
                advancement_rubric : {advancement_rubric}
                
                Return a JSON object like this:
                {{
                    "score": number (between 1-100, whole number)
                    "advancement_level": number (between 1-100, whole number)
                }}
                
                these two numbers will then be used to evaluate the points the lesson will be worth, to then update skill rating the lesson belongs to. the points will be evaluated manually you don't have to return it.
                """
            
    results = gemini_AI(prompt)
    
    results['points'] = min(int((results['score'] / 100) * results['advancement_level'] * 1.5), 30) # the 1.5 multiplier is to make sure the points are more spread out across the range, and the min with 30 is to make sure the points don't exceed 30.
    return results
    
def update_parent_category_rating(category):
    parent_category = category.parent    
    parent_category.rating = sum(child.rating for child in parent_category.children.all()) // parent_category.children.all().count() # used // to make it as integer. 
    parent_category.save()
    return 

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
            print(serializer.errors)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoginView(APIView):

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                print(user)
                refresh = RefreshToken.for_user(user)
                content = {'refresh': str(refresh), 'access': str(refresh.access_token),'user': UserSerializer(user).data}
                return Response(content, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Home(APIView):
    def get(self, request):
        content = Category.objects.annotate()
        return Response({"categories":CategorySerializer(content, many=True).data})
    
class CategoriesIndex(APIView):
    serializer_class = CategorySerializer
    categories = Category.objects.all()
    categories3 = Category.objects.filter(hierarchy=3)
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
            cat_lessons = Lesson.objects.filter(user=request.user, category=category_id)
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
            print(err)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class CategoryLessons(APIView):
    serializer_class = LessonSerializer
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        lesson_categoy_results = lesson_category_check(request.data, category)
        if not lesson_categoy_results['belongs'] :
            return Response({"failed":"failed"})     

        categories = {
        "grandparent-category": category.parent.parent.__str__(),
        "parent-category": category.parent.__str__(),
        "child-category_current": category.__str__()
        }
        
        lesson_results = lesson_score(request.data, categories)
        data = request.data.copy()
        data["score"] = lesson_results['score']
        data["points"] = lesson_results['points']
                
        try:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save(user_id=request.user.id)
                
                category.rating = min( category.rating + serializer.data['points'], 100 ) # to make sure the rating doesn't exceed 100.
                category.save()
                update_parent_category_rating(category)
                
                category_serialized = CategorySerializer(category)
                queryset =  Lesson.objects.filter(user=request.user, category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                "category": category_serialized.data,
                "lessons": serializer.data
                }, status=status.HTTP_200_OK)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LessonDetail(APIView):
    serializer_class = LessonSerializer
    
    def put(self, request, category_id, lesson_id):
        category = get_object_or_404(Category, id=category_id)
        lesson_categoy_results = lesson_category_check(request.data, category) # check if the updated lesson still belongs to the same category.
        if not lesson_categoy_results['belongs']:
            return Response({"failed":"failed"})  
        
        categories = {
            "grandparent-category": category.parent.parent.__str__(),
            "parent-category": category.parent.__str__(),
            "child-category_current": category.__str__()
            }
        
        updated_lesson_results = lesson_score(request.data, categories)
        data = request.data.copy()
        data["score"] = updated_lesson_results['score']
        data["points"] = updated_lesson_results['points']    
        
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            old_points = lesson.points
            print("old points", old_points)
            serializer = self.serializer_class(lesson, data=data)
            if serializer.is_valid():
                serializer.save()
                
                print("new points", serializer.data['points'])
                print("category rating before update", category.rating)
                category.rating = min( category.rating + (serializer.data['points'] - old_points), 100 ) # to make sure rating doesn't exceed 100.
                category.save()
                update_parent_category_rating(category)
                
                print("category rating after update", category.rating)
                
                queryset = Lesson.objects.filter(user=request.user, category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                    "category": CategorySerializer(category).data,
                    "lessons":serializer.data,
                    "lesson": LessonSerializer(lesson).data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, category_id, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            print("lesson to delete", lesson)
            lesson_points = lesson.points
            print("lesson points", lesson_points, type(lesson_points))
            lesson.delete()
            
            category = get_object_or_404(Category, id=category_id)
            category.rating = max(( category.rating - lesson_points), 0 ) # to make sure the rating doesn't go below 0.
            category.save()
            update_parent_category_rating(category)
            
            queryset = Lesson.objects.filter(user=request.user, category=category_id)
            serializer = self.serializer_class(queryset, many=True)
            return Response({
                "category": CategorySerializer(category).data,
                "lessons": serializer.data}, status=status.HTTP_200_OK)
        except Exception as err:
            print(err)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class VerifyUserView(APIView):
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            try:
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh),'access': str(refresh.access_token),'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
            except Exception as token_error:
                return Response({"detail": "Failed to generate token.", "error": str(token_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            return Response({"detail": "Unexpected error occurred.", "error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardIndex(APIView):
    def get(self, request):
        try:
            total_skills = Category.objects.filter(hierarchy=3).count()
            mastered_skills = Category.objects.filter(hierarchy=3, rating__gte=80).count()
            in_progress_skills = total_skills - mastered_skills
            total_lessons = Lesson.objects.filter(user=request.user).count()
            category_technical_mastery= Category.objects.get(name="Technical Mastery")
            category_soft_skills= Category.objects.get(name="Soft & Interpersonal Skills")
            category_personal_skills= Category.objects.get(name="Personal & Habitual Skills")
            
            stats =  [
                {
                    "name": "Total Skills",
                    "icon": "Target",
                    "data": total_skills,
                    "description": "Across all categories"
                },
                {
                    "name": "In Progress",
                    "icon": "TrendingUp",
                    "data": in_progress_skills,
                    "description": "Currently learning"
                },  
                {
                    "name": "Mastered Skills",
                    "icon": "Award",
                    "data": mastered_skills,
                    "description": "Skills mastered"
                },
                {
                    "name": "Lessons",
                    "icon": "BookOpen",
                    "data": total_lessons,
                    "description": "Total entries"
                    }
                ]
            
            return Response({'userStats': stats,
                            'technicalMasteryOverview': category_technical_mastery.children.all().values('name', 'rating'),
                            'softSkillsOverview': category_soft_skills.children.all().values('name', 'rating'),
                            'personalSkillsOverview': category_personal_skills.children.all().values('name', 'rating')}, 
                            status=status.HTTP_200_OK)
        except Exception as err:
            print(err)
            return Response({'error':str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        