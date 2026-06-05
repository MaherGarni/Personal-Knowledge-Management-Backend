from unicodedata import category

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Category, Lesson, UserProfile
from .serializers import CategorySerializer, LessonSerializer, UserSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404
from google import genai
from google.genai.types import GenerateContentConfig
from google.genai.errors import ServerError
import json
# import User model, UserSerializer, and RefreshToken...
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
# new import!
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.utils import timezone 
from django.db.models import F, Sum
import sys
from rest_framework.exceptions import ValidationError


daily_reset_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

client = genai.Client()

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


def seed_user(user):
    category_level_1 = [
            { 'name' : 'Technical Mastery',             'parent': None, 'color': "#A5C3F0", 'hierarchy': 1, 'rating': 0, 'user': user },
            { 'name' : 'Soft & Interpersonal Skills',   'parent': None, 'color': '#FCD34D', 'hierarchy': 1, 'rating': 0, 'user': user },
            { 'name' : 'Personal & Habitual Skills',    'parent': None, 'color': '#86EFAC', 'hierarchy': 1, 'rating': 0, 'user': user } 
            ]
    
    for category_data in category_level_1:
        Category.objects.create(**category_data)
    
    category_technical_mastery = Category.objects.get(name='Technical Mastery', user=user)
    category_soft_skills       = Category.objects.get(name='Soft & Interpersonal Skills', user=user)
    category_personal_skills   = Category.objects.get(name='Personal & Habitual Skills', user=user)
    
    technical_mastery_categories = [
            { 'name' : 'Core Programming & CS Fundamentals',   'parent': category_technical_mastery, 'color': '#aec7e8', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Frontend Development',                 'parent': category_technical_mastery, 'color': '#1f77b4', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Backend Development',                  'parent': category_technical_mastery, 'color': '#17becf', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Software Design & Architecture',       'parent': category_technical_mastery, 'color': '#c7c7c7', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Cloud, DevOps & Infrastructure',       'parent': category_technical_mastery, 'color': '#9467bd', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Testing & Quality Assurance',          'parent': category_technical_mastery, 'color': '#8c564b', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Databases & Data Management',          'parent': category_technical_mastery, 'color': '#e377c2', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'AI / Machine Learning & Data Skills',  'parent': category_technical_mastery, 'color': '#7f7f7f', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Security & Cybersecurity Awareness',   'parent': category_technical_mastery, 'color': '#bcbd22', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'System Design & Scalability',          'parent': category_technical_mastery, 'color': '#ffbb78', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Software Engineering Practices',       'parent': category_technical_mastery, 'color': '#d62728', 'hierarchy': 2, 'rating': 0, 'user': user },
            ] 

    soft_skills_categories = [ 
            { 'name' : 'Communication Skills',                 'parent': category_soft_skills, 'color': '#ff9896', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Collaboration & Teamwork',             'parent': category_soft_skills, 'color': '#c49c94', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Problem Solving & Critical Thinking',  'parent': category_soft_skills, 'color': '#f7b6d2', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Leadership',                           'parent': category_soft_skills, 'color': '#dbdb8d', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Time & Task Management',               'parent': category_soft_skills, 'color': '#9edae5', 'hierarchy': 2, 'rating': 0, 'user': user },
            ]
    
    personal_skills_categories = [
            { 'name' : 'Deep Work & Focus',                    'parent': category_personal_skills, 'color': '#17becf', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Discipline & Consistency',             'parent': category_personal_skills, 'color': '#bcbd22', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Professionalism & Work Ethics',        'parent': category_personal_skills, 'color': '#ff9896', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Documentation & Knowledge Management', 'parent': category_personal_skills, 'color': '#c5b0d5', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Self-Reflection & Improvement',        'parent': category_personal_skills, 'color': '#ff7f0e', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Mental & Physical Well-being',         'parent': category_personal_skills, 'color': '#2ca02c', 'hierarchy': 2, 'rating': 0, 'user': user },
            { 'name' : 'Curiosity & Continuous Learning',      'parent': category_personal_skills, 'color': '#8c564b', 'hierarchy': 2, 'rating': 0, 'user': user },
            ]
    
    for category_data in technical_mastery_categories:
        Category.objects.create(**category_data)
        
    for category_data in soft_skills_categories:
        Category.objects.create(**category_data)
    
    for category_data in personal_skills_categories:
        Category.objects.create(**category_data)
        

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
    parent_category.rating = sum(child.rating for child in parent_category.children.all()) // parent_category.children.all().count() if parent_category.children.all().count() > 0  else  0 # to avoid division by zero
    parent_category.save()


def get_user_limits (user):
    user_data = UserSerializer(user).data
    user_limits, _ = UserProfile.objects.get_or_create(user=user)  # _ discard the second element returned from ger_or_create()
    user_data['dailyAiLimit']= user_limits.daily_ai_limit
    user_data['dailyCallsCounter']= user_limits.daily_calls_counter
    return user_data
    
def update_user_limits(user, user_data):
    UserProfile.objects.filter(user=user).update(daily_calls_counter=F('daily_calls_counter') + 1)
    UserProfile.objects.filter(user=user).update(last_call_date=timezone.now())
    user_limits = UserProfile.objects.get(user=user)
    user_data['dailyAiLimit'] = user_limits.daily_ai_limit
    user_data['dailyCallsCounter'] = user_limits.daily_calls_counter
    
def check_reset_limit(user, user_data):
    user_limits = UserProfile.objects.get(user=user)
    if user_limits.last_call_date and user_limits.last_call_date < daily_reset_time :
        user_limits.daily_calls_counter = 0
        user_limits.save()
        user_data['dailyAiLimit'] = user_limits.daily_ai_limit
        user_data['dailyCallsCounter'] = user_limits.daily_calls_counter
    
        

    
        


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
            
            seed_user(user)  # Seed categories for the new user
            
            user_data = get_user_limits(user)
            
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        except ValidationError as err:
            return Response({'error' : str(err) } ,status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoginView(APIView):

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is None:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user_data = get_user_limits(user)
            check_reset_limit(user, user_data)    
            
            if user:
                refresh = RefreshToken.for_user(user)
                content = {'refresh': str(refresh), 'access': str(refresh.access_token),'user': user_data}
                return Response(content, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyUserView(APIView):
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            try:
                refresh = RefreshToken.for_user(user)
                
                user_data = get_user_limits(user)
                check_reset_limit(user, user_data)  
                
                return Response({'refresh': str(refresh),'access': str(refresh.access_token),'user': user_data}, status=status.HTTP_200_OK)
            except Exception as token_error:
                return Response({"detail": "Failed to generate token.", "error": str(token_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            print(err)
            return Response({"detail": "Unexpected error occurred.", "error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

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
            queryset = Category.objects.filter(user=request.user, hierarchy=1)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            data = request.data.copy()
            data['user'] = request.user.id

            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save(user_id=request.user.id)
                updated_categories = Category.objects.filter(hierarchy=1, user=request.user)
                response_data = self.serializer_class(updated_categories, many=True)
                return Response(response_data.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'eroor':str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CategoryDetail(APIView):
    serializer_class = CategorySerializer   
    
    def get(self, request, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            category_lessons = Lesson.objects.filter(user=request.user, category=category_id)
            serialized_lessons = LessonSerializer(category_lessons, many=True)
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
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = self.serializer_class(category, data=data)
            if serializer.is_valid():
                serializer.save()
                queryset = Category.objects.filter(hierarchy=1, user=request.user)
                updated_categories = self.serializer_class(queryset, many=True).data
                return Response(updated_categories, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, category_id):
        try:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            update_parent_category_rating(category)
            queryset = Category.objects.filter(hierarchy=1, user=request.user)
            updated_categories = self.serializer_class(queryset, many=True).data
            return Response(updated_categories, status=status.HTTP_200_OK)
        except Exception as err:
            print(err)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class CategoryLessons(APIView):
    serializer_class = LessonSerializer
    def post(self, request, category_id):    
        category = get_object_or_404(Category, id=category_id, )
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
                
                user_data = UserSerializer(request.user).data
                update_user_limits(request.user, user_data)
                
                category_serialized = CategorySerializer(category)
                queryset =  Lesson.objects.filter(user=request.user, category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                "category": category_serialized.data,
                "lessons": serializer.data,
                "user": user_data
                }, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ServerError as ai_error:
            return Response({"error": "ai_unavailable"}, status=503)
        except Exception:
            return Response({"error": "server_error"}, status=500)
        
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
            serializer = self.serializer_class(lesson, data=data)
            if serializer.is_valid():
                serializer.save()
                
                category.rating = min( category.rating + (serializer.data['points'] - old_points), 100 ) # to make sure rating doesn't exceed 100.
                category.save()
                update_parent_category_rating(category)
                
                user_data = UserSerializer(request.user).data
                update_user_limits(request.user, user_data)
                
                queryset = Lesson.objects.filter(user=request.user, category=category_id)
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                    "category": CategorySerializer(category).data,
                    "lessons":serializer.data,
                    "lesson": LessonSerializer(lesson).data,
                    "user" : user_data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ServerError as ai_error:
            return Response({"error": "ai_unavailable"}, status=503)
        except Exception:
            return Response({"error": "server_error"}, status=500)    
        
    def delete(self, request, category_id, lesson_id):
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.delete()

            category_total_points = Lesson.objects.filter(user=request.user, category=category_id).aggregate(Sum('points'))
            
            category = get_object_or_404(Category, id=category_id)
            category.rating = min(category_total_points['points__sum'], 100 ) if category_total_points['points__sum'] else 0 # to make sure rating don't exceed 100
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
        
        
class DashboardIndex(APIView):
    def get(self, request):
        try:
            total_skills = Category.objects.filter(hierarchy=3, user=request.user).count()
            mastered_skills = Category.objects.filter(hierarchy=3, user=request.user, rating__gte=80).count()
            in_progress_skills = total_skills - mastered_skills
            total_lessons = Lesson.objects.filter(user=request.user).count()
            category_technical_mastery= Category.objects.get(name="Technical Mastery", user=request.user)
            category_soft_skills= Category.objects.get(name="Soft & Interpersonal Skills", user=request.user)
            category_personal_skills= Category.objects.get(name="Personal & Habitual Skills", user=request.user)

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
        
        