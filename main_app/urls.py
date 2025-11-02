from django.urls import path
from .views import Home, CategoriesIndex, CategoryDetail

urlpatterns = [
    path('', Home.as_view(), name='home'), #comment
    path('categories/', CategoriesIndex.as_view(), name='categories-index'),
    path('categories/<int:category_id>/', CategoryDetail.as_view(), name='category-detail'),
]