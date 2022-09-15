from django.urls import path

from . import views

urlpatterns = [
    path('questionQuery',views.QuestionQueryService),
    path('vote', views.VoteService),
    path('saveIndexFile', views.SaveIndexFile),
    path('restartService',views.RestartService),
    path('keepConnection', views.KeepConnection),
]