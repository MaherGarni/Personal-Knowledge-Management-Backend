from django.urls import path
from .views import Home, CategoriesIndex, CategoryDetail, CategoryLessons, LessonDetail, CreateUserView, LoginView, VerifyUserView

urlpatterns = [
    path('users/signup/', CreateUserView.as_view(), name='signup'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
    path('', Home.as_view(), name='home'), #comment
    path('categories/', CategoriesIndex.as_view(), name='categories-index'),
    path('categories/<int:category_id>/', CategoryDetail.as_view(), name='category-detail'),
    path('categories/<int:category_id>/lessons/', CategoryLessons.as_view(), name='category-lessons'),
    path('categories/<int:category_id>/lessons/<int:lesson_id>/', LessonDetail.as_view(), name='lesson-detail'),
]