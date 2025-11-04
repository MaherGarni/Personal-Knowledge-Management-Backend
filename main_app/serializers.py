from rest_framework import serializers
from .models import Category, Lesson
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    # Add a password field, make it write-only
    # prevents allowing 'read' capabilities (returning the password via api response)
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']  
        )

        return user

        
class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)
    children=serializers.SerializerMethodField()
    # lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data
    
class LessonSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Lesson
        fields = '__all__'