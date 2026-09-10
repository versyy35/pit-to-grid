from django.urls import path
from . import views

urlpatterns = [
    path('races/', views.RaceListView.as_view(), name='race-list'),
    path('races/<int:race_id>/laps/', views.RaceLapsView.as_view(), name='race-laps'),
    path('races/<int:race_id>/pitstops/', views.RacePitStopsView.as_view(), name='race-pitstops'),
    path('races/<int:race_id>/results/', views.RaceResultsView.as_view(), name='race-results'),
    path('seasons/<int:year>/champion/', views.SeasonChampionView.as_view(), name='season-champion'),
    path('races/<int:race_id>/session/', views.RaceSessionView.as_view(), name='race-session'),
    path('races/<int:race_id>/', views.RaceDetailView.as_view(), name='race-detail'),
]
