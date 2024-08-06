from django import forms
from .models import Meeting
from django.contrib.auth import get_user_model

User = get_user_model()


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'body',
            # 'tags',
            'reporter',
            'minutes_document',
            'date_debut',
            'date_fin',
            'meeting_status',
            'deadline_hours'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la réunion',
                'required': 'required'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Contenu de la réunion',
                'required': 'required'
            }),
            # 'tags': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Tags (séparés par des virgules)',
            #     'required': 'required'
            # }),
            'reporter': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Gestionnaire du compte rendu',
                'required': 'required'
            }),
            'minutes_document': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Télécharger le procès verbal'
            }),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Date et heure de début de la réunion',
                # 'required': 'required',
                'type': 'datetime-local',
                'value': 'date_debut'
            }),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Date et heure de fin de la réunion',
                # 'required': 'required',
                'type': 'datetime-local',
                'value': 'date_fin'
            }),
            'meeting_status': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Statut de la réunion',
                'required': 'required'
            }),
            'deadline_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Délai de soumission (heures)',
                'required': 'required'
            }),
        }

class AddParticipantForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        label="Participant",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Sélectionnez un participant',
            'required': 'required'
        })
    )
    number_verify = forms.CharField(
        max_length=50, 
        label="Numéro de participation",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le numéro de participation',
            'required': 'required'
        })
    )

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting', None)
        super().__init__(*args, **kwargs)
        self.fields['participant'].queryset = User.objects.exclude(participations__meeting=self.meeting)