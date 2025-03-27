from django.urls import path
from .views import ProfileView, ProfileSingleView, RegisterView, LoginView, BusinessProfileListView, CustomerProfileListView

urlpatterns = [
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('profile/', ProfileView.as_view(), name='profile-list'),
    path('profile/<int:user>/', ProfileSingleView.as_view(), name='profile-detail'),

    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles'),

]