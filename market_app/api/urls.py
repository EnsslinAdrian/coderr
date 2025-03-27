from django.urls import path
from .views import OrderView, OrderSingleView, OffersFrontendCompatibleView, OfferSingleView, \
OfferOptionSingleView, ReviewView, ReviewSingleView, BaseSingleView, BaseView, OrderCountView, \
CompletedOrderCountView

urlpatterns = [
    path('offers/', OffersFrontendCompatibleView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferSingleView.as_view(), name='offers-details'),
    path('offerdetails/<int:pk>/', OfferOptionSingleView().as_view()),

    path('orders/', OrderView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrderSingleView.as_view(), name='orders-details'),

    path('order-count/<int:pk>/', OrderCountView.as_view()),

    path('completed-order-count/<int:pk>/', CompletedOrderCountView.as_view(), name='completed-order-count-details'),

    path('reviews/', ReviewView.as_view(), name='reviews-list'),
    path('reviews/<int:pk>/', ReviewSingleView.as_view(), name='reviews-details'),

    path('base-info/', BaseView.as_view()),
    path('base-info/<int:pk>/', BaseSingleView.as_view()),
]