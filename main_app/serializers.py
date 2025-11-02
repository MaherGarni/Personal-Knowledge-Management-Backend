from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)
    children=serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data