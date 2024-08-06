from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from userauths.models import Profile
from .models import Meeting, MeetingReview, Participation
from .forms import MeetingForm

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings

from .forms import AddParticipantForm
from django.views import View
from django.db import IntegrityError

# from django.http import HttpResponse, Http404
# from django.conf import settings
# import os


class MeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = "meetings/acceuil.html"
    context_object_name = "meetings"
    paginate_by = 6
    login_url = 'userauths-sign-in'

    def get_queryset(self):
        return Meeting.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_meetings'] = Meeting.objects.count()
        return context

class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    template_name = "meetings/meeting_detail.html"
    context_object_name = "meeting"
    login_url = 'userauths-sign-in'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_meetings'] = Meeting.objects.order_by('-created_at')[:6]
        context['all_tags'] = Tag.objects.all()
        context['participations'] = self.object.participations.select_related('participant')
        return context

class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    form_class = MeetingForm
    template_name = "meetings/meeting_form.html"
    success_url = reverse_lazy("aguipex-home")
    login_url = 'userauths-sign-in'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Réunion créée avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la création de la réunion.")
        return super().form_invalid(form)

class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = "meetings/meeting_form.html"
    success_url = reverse_lazy("aguipex-home")
    login_url = 'userauths-sign-in'

    def form_valid(self, form):
        messages.success(self.request, "Réunion mise à jour avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la mise à jour de la réunion.")
        return super().form_invalid(form)

class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    model = Meeting
    template_name = "meetings/meeting_confirm_delete.html"
    context_object_name = "meeting"
    success_url = reverse_lazy("aguipex-home")
    login_url = 'userauths-sign-in'

    def delete(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.tags.clear()
        messages.success(self.request, "Réunion supprimée avec succès.")
        return super().delete(request, *args, **kwargs)

class MeetingListByTagView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'meetings/meeting_list_by_tag.html'
    context_object_name = 'meetings'
    login_url = 'userauths-sign-in'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return Meeting.objects.filter(tags__slug=slug)

class PersonnelListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "meetings/personnels.html"
    context_object_name = "personnels"
    login_url = 'userauths-sign-in'

def add_review(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        review = request.POST.get('review')

        if full_name and review:
            MeetingReview.objects.create(
                full_name=full_name,
                meeting=meeting,
                review=review
            )
            messages.success(request, "Merci pour votre avis !")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return redirect('meeting_detail', pk=meeting_id)

# def add_review(request, meeting_id):
#     meeting = get_object_or_404(Meeting, pk=meeting_id)

#     if request.method == 'POST':
#         full_name = request.POST.get('full_name')
#         review = request.POST.get('review')

#         if full_name and review:
#             MeetingReview.objects.create(
#                 full_name=full_name,
#                 meeting=meeting,
#                 review=review
#             )
#             response = {'status': 'success', 'message': 'Merci pour votre avis !'}
#         else:
#             response = {'status': 'error', 'message': 'Veuillez remplir tous les champs.'}

#         return JsonResponse(response)

def validate_presence(request, meeting_id):
    if request.method == 'POST':
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        participant_id = request.POST.get('participant')
        number_verify = request.POST.get('number_verify')

        try:
            participation = Participation.objects.get(
                meeting=meeting,
                participant_id=participant_id
            )
            if participation.number_verify != number_verify:
                return JsonResponse({'status': 'error', 'message': "Le numéro saisi ne vous appartient pas. Merci de vérifier ou de contacter l'admin."})
            elif participation.status == 'present':
                return JsonResponse({'status': 'error', 'message': "Vous avez déjà confirmé votre présence."})
            else:
                participation.status = 'present'
                participation.save()
                return JsonResponse({'status': 'success', 'message': "Merci pour votre présence."})
        except Participation.DoesNotExist:
            if Participation.objects.filter(number_verify=number_verify).exists():
                return JsonResponse({'status': 'error', 'message': "Le numéro est déjà utilisé."})
            else:
                return JsonResponse({'status': 'error', 'message': "Le numéro saisi ne vous appartient pas. Merci de vérifier ou de contacter l'admin."})

    return JsonResponse({'status': 'error', 'message': "Méthode non autorisée."})

def sarch_view(request):
    query = request.GET.get('q')
    meetings = Meeting.objects.filter(title__icontains=query).order_by('-created_at')
    context = {
        'query':query,
        'meetings':meetings
    }
    return render(request, 'meetings/search.html', context)



# def download_model(request):
#     file_path = os.path.join(settings.MEDIA_ROOT, 'modele', 'file.xlsx')
    
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#             response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
#             return response
#     else:
#         raise Http404("Fichier non trouvé")

def participant_list(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    participants_present = Participation.objects.filter(meeting=meeting, status='present')
    
    return render(request, 'meetings/participant.html', {'participants_present': participants_present, 'meeting': meeting})


def download_participants_list(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    participants_present = Participation.objects.filter(meeting=meeting, status='present')

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="participants_meeting_{}.pdf"'.format(meeting_id)

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title and header information
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, f"Liste des participants pour la réunion: {meeting.title}")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "MINISTERE DU COMMERCE DE L’INDUSTRIE ET DES PME")
    p.drawString(100, height - 90, "Conakry le………………..")
    p.drawString(100, height - 110, "Réf………….MCIPME/DGA/DG/AGUIPEX/2024")

    # Table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 140, "Nom")
    p.drawString(200, height - 140, "Email")
    p.drawString(350, height - 140, "Fonction")
    p.drawString(500, height - 140, "Téléphone")

    # Draw table lines
    p.line(50, height - 145, 550, height - 145)

    # Participants data
    y = height - 160
    p.setFont("Helvetica", 12)
    for participation in participants_present:
        p.drawString(50, y, participation.participant.profile.full_name)
        p.drawString(200, y, participation.participant.email)
        p.drawString(350, y, participation.participant.profile.fonction)
        p.drawString(500, y, participation.participant.profile.phone)
        y -= 20

    # Footer contact information
    p.setFont("Helvetica", 10)
    footer_y = 50
    p.drawString(100, footer_y, "Immeuble Horizon 3ème étage 5ème Avenue Sandervalia Commune de Kaloum")
    footer_y -= 15
    p.drawString(100, footer_y, "BP 6822P Conakry République de Guinée")
    footer_y -= 15
    p.drawString(100, footer_y, "Tel: (224) 611 75 65 52")
    footer_y -= 15
    p.drawString(100, footer_y, "Site web: www.aguipex.gov.gn/ Email: contact@aguipex.gov.gn")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response


# def download_participants_list(request, meeting_id):
#     meeting = get_object_or_404(Meeting, pk=meeting_id)
#     participants_present = Participation.objects.filter(meeting=meeting, status='present')

#     # Create the HttpResponse object with the appropriate PDF headers.
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="participants_meeting_{meeting_id}.pdf"'

#     # Create the PDF object, using the response object as its "file."
#     p = canvas.Canvas(response, pagesize=letter)
#     width, height = letter

#     # Add watermark image
#     watermark_path = settings.STATICFILES_DIRS[0] + '/assets/img/pageParticipant/branding.png'
#     p.drawImage(watermark_path, 0, 0, width, height, mask='auto')

#     # Add first image (converted to PNG)
#     img_path_1 = settings.STATICFILES_DIRS[0] + '/assets/img/pageParticipant/image1.png'
#     p.drawImage(img_path_1, 100, height - 220, width=200, height=50, mask='auto')

#     # Add first header
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(100, height - 250, "MINISTERE DU COMMERCE,")
#     p.drawString(100, height - 270, "DE L’INDUSTRIE ET DES PME")
#     p.drawString(100, height - 290, "Réf………….MCIPME/DGA/DG/AGUIPEX/2024")

#     # Add second image (converted to PNG)
#     img_path_2 = settings.STATICFILES_DIRS[0] + '/assets/img/pageParticipant/image2.png'
#     p.drawImage(img_path_2, 100, height - 340, width=200, height=50, mask='auto')

#     # Add second header
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(100, height - 370, "Conakry, le………………..")

#     # Table headers
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(50, height - 420, "Nom")
#     p.drawString(200, height - 420, "Email")
#     p.drawString(350, height - 420, "Fonction")
#     p.drawString(500, height - 420, "Téléphone")

#     # Draw table lines
#     p.line(50, height - 425, 550, height - 425)

#     # Participants data
#     y = height - 440
#     p.setFont("Helvetica", 12)
#     for participation in participants_present:
#         p.drawString(50, y, participation.participant.profile.full_name)
#         p.drawString(200, y, participation.participant.email)
#         p.drawString(350, y, participation.participant.profile.fonction)
#         p.drawString(500, y, participation.participant.profile.phone)
#         y -= 20

#     # Footer contact information
#     p.setFont("Helvetica", 10)
#     footer_y = 50
#     footer_text = [
#         "Immeuble Horizon 3ème étage 5ème Avenue Sandervalia Commune de Kaloum",
#         "BP 6822P Conakry République de Guinée",
#         "Tel: (224) 611 75 65 52",
#         "Site web: www.aguipex.gov.gn/ Email: contact@aguipex.gov.gn"
#     ]
#     text_width = 400  # Adjust as necessary
#     for line in footer_text:
#         text_object = p.beginText(width/2 - text_width/2, footer_y)
#         text_object.setFont("Helvetica", 10)
#         text_object.textLines(line)
#         p.drawText(text_object)
#         footer_y -= 15

#     # Close the PDF object cleanly.
#     p.showPage()
#     p.save()

#     return response

class AddParticipantView(LoginRequiredMixin, View):
    def get(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        form = AddParticipantForm(meeting=meeting)
        return render(request, 'meetings/add_participant.html', {'form': form, 'meeting': meeting})

    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        form = AddParticipantForm(request.POST, meeting=meeting)
        if form.is_valid():
            participant = form.cleaned_data['participant']
            number_verify = form.cleaned_data['number_verify']
            try:
                Participation.objects.create(participant=participant, meeting=meeting, number_verify=number_verify)
                messages.success(request, "Participant ajouté avec succès.")
            except IntegrityError:
                messages.error(request, "Erreur : Ce numéro de participation est déjà utilisé.")
            return redirect(reverse('meeting_detail', args=[pk]))
        return render(request, 'meetings/add_participant.html', {'form': form, 'meeting': meeting})
    
class ScheduledParticipantsView(View):
    def get(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        scheduled_participants = Participation.objects.filter(meeting=meeting)
        context = {
            'meeting': meeting,
            'scheduled_participants': scheduled_participants,
        }
        return render(request, 'meetings/scheduled_participants.html', context)
    

def generate_participant_list_pdf(request, meeting_id):
    meeting = Meeting.objects.get(pk=meeting_id)
    participants = Participation.objects.filter(meeting=meeting)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="participants_{meeting_id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 50, f"Liste des participants prevu pour la réunion: {meeting.title}")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, "MINISTERE DU COMMERCE DE L’INDUSTRIE ET DES PME")
    p.drawString(100, height - 90, "Conakry le………………..")
    p.drawString(100, height - 110, "Réf………….MCIPME/DGA/DG/AGUIPEX/2024")


      # Table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 140, "Nom")
    p.drawString(200, height - 140, "Email")
    p.drawString(350, height - 140, "Fonction")
    p.drawString(500, height - 140, "Téléphone")

    # Draw table lines
    p.line(50, height - 145, 550, height - 145)



      # Participants data
    y = height - 160
    p.setFont("Helvetica", 12)
    for participant in participants:
        p.drawString(50, y, participant.participant.profile.full_name)
        p.drawString(200, y, participant.participant.email)
        p.drawString(350, y, participant.participant.profile.fonction)
        p.drawString(500, y, participant.participant.profile.phone)
        y -= 20


        # Footer contact information
    p.setFont("Helvetica", 10)
    footer_y = 50
    p.drawString(100, footer_y, "Immeuble Horizon 3ème étage 5ème Avenue Sandervalia Commune de Kaloum")
    footer_y -= 15
    p.drawString(100, footer_y, "BP 6822P Conakry République de Guinée")
    footer_y -= 15
    p.drawString(100, footer_y, "Tel: (224) 611 75 65 52")
    footer_y -= 15
    p.drawString(100, footer_y, "Site web: www.aguipex.gov.gn/ Email: contact@aguipex.gov.gn")

    p.showPage()
    p.save()
    return response