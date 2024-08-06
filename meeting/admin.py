from django.contrib import admin
from meeting.models import Meeting, Participation, MeetingReview, Wishlist


class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", 'reporter', 'date_debut', 'date_fin', 'duration', 'meeting_status']
    list_display_links = ['title', 'reporter']
    search_fields = ['title']


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ["number_verify", "participant", 'meeting', 'status']
    search_fields = ["number_verify", "participant"]


class MeetingReviewAdmin(admin.ModelAdmin):
    list_display = ["full_name", "meeting", 'review']


class wishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "meeting"]


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(MeetingReview, MeetingReviewAdmin)
admin.site.register(Wishlist, wishlistAdmin)
