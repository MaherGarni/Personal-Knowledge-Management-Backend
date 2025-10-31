from rest_framework import serializers
from .models import Category


class GrandparentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ParentCategorySerializer(serializers.ModelSerializer):
    parent = GrandparentSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "parent"]

class CategorySerializer(serializers.ModelSerializer):
    parent = ParentCategorySerializer(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'