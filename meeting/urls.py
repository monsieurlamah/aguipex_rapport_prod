from django.urls import path
from .views import AddParticipantView, MeetingListView, MeetingDetailView, MeetingCreateView, MeetingUpdateView, MeetingDeleteView, \
    PersonnelListView, MeetingListByTagView, ScheduledParticipantsView, add_review, download_participants_list, generate_participant_list_pdf, participant_list, sarch_view, validate_presence

urlpatterns = [
    path('', MeetingListView.as_view(), name="aguipex-home"),
    path('meeting/<int:pk>/', MeetingDetailView.as_view(), name="meeting_detail"),
    path('meeting/new/', MeetingCreateView.as_view(), name="meeting_create"),
    path('meeting/<int:pk>/edit/', MeetingUpdateView.as_view(), name="meeting_update"),
    path('meeting/<int:pk>/delete/', MeetingDeleteView.as_view(), name='meeting_delete'),
    path('tag/<slug:slug>/', MeetingListByTagView.as_view(), name='meeting_list_by_tag'),
    path('personnels/', PersonnelListView.as_view(), name='aguipex-personnel'),
    path('meeting/<int:meeting_id>/add_review/', add_review, name='add_review'),
    path('meeting/<int:meeting_id>/validate_presence/', validate_presence, name='validate_presence'),
    path('recherche/', sarch_view, name="aguipex-search"),
    # path('download-model/', download_model, name='download_model_url'),
    path('meeting/<int:meeting_id>/participants/', participant_list, name='participant_list'),
    path('meeting/<int:meeting_id>/download_participant_list/', download_participants_list, name='download_participants_list'),
    path('meetings/<int:pk>/add_participant/', AddParticipantView.as_view(), name='add_participant'),
    path('meeting/<int:pk>/scheduled-participants/', ScheduledParticipantsView.as_view(), name='scheduled_participants'),
    path('meeting/<int:meeting_id>/participants/pdf/', generate_participant_list_pdf, name='participants_pdf'),







]
