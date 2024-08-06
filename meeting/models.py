from datetime import timedelta
from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from common.models import TimeStampedModel
from django.utils import timezone

User = get_user_model()

STATUS = (
    ('programmer', 'Programmer'),
    ('en_cours', 'En cours'),
    ('terminer', 'Terminer'),
)

RATING = (
    (1, '★✩✩✩✩'),
    (2, '★★✩✩✩'),
    (3, '★★★✩✩'),
    (4, '★★★★✩'),
    (5, '★★★★★'),
)


class Meeting(TimeStampedModel):
    title = models.CharField(verbose_name=_("Titre"), max_length=250)
    slug = AutoSlugField(populate_from="title", unique=True)
    body = models.TextField(verbose_name=_("Réunion"))
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(User, verbose_name=_("Auteur"), on_delete=models.CASCADE, related_name="author_meetings")
    reporter = models.ForeignKey(User, verbose_name=_("Gestionnaire compte rendu"), on_delete=models.CASCADE,
                                 related_name="reporter_meetings")
    minutes_document = models.FileField(null=True, blank=True, verbose_name=_("Procès verbal"))
    date_debut = models.DateTimeField(blank=True, null=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    meeting_status = models.CharField(choices=STATUS, max_length=15, default="programmer",
                                      verbose_name="Statut de la réunion")
    deadline_hours = models.IntegerField(verbose_name=_("Délai de soumission (heures)"), default=24)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not (
                self.author.is_superuser
                or self.author.is_staff
                # or self.author.profile.occupation == Profile.Occupation.RESPONSABLE
        ):
            raise ValueError(
                "Seuls les superutilisateurs ou les membres du personnel peuvent créer des réunions."
            )

        if self.date_fin:
            deadline = self.date_fin + timezone.timedelta(hours=self.deadline_hours)
            if self.reporter and timezone.now() > deadline:
                # Logique pour pénaliser le reporter ici
                print(f"Le reporter {self.reporter.username} a manqué le délai pour soumettre le rapport.")

        super().save(*args, **kwargs)

    def has_reporter_missed_deadline(self):
        if self.date_fin:
            deadline = self.date_fin + timezone.timedelta(hours=self.deadline_hours)
            return self.reporter and timezone.now() > deadline
        return False

    def duration(self):
        if self.date_debut and self.date_fin:
            duration = self.date_fin - self.date_debut
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes = remainder // 60

            if int(hours) == 0:
                return f"{int(minutes)}min"
            else:
                return f"{int(hours)}h{int(minutes)}min"

        return "Durée indéterminée"
    
    def rapport_deadline(self):
        """
        Retourne la date et l'heure limite pour soumettre le rapport en tenant compte du délai de soumission
        et de la date de fin de la réunion.
        """
        if self.date_fin and self.deadline_hours is not None:
            deadline = self.date_fin + timedelta(hours=self.deadline_hours)
            return deadline
        return None

    def get_tags_display(self):
        return ", ".join(tag.name for tag in self.tags.all())

    class Meta:
        verbose_name = _("Réunion")
        verbose_name_plural = _("Réunions")


class Participation(TimeStampedModel):
    number_verify = models.CharField(max_length=50, unique=True, verbose_name=_("Numéro de participation"))
    participant = models.ForeignKey(User, verbose_name=_("Participant"), on_delete=models.CASCADE,
                                    related_name="participations")
    meeting = models.ForeignKey(Meeting, verbose_name=_("Réunion"), on_delete=models.CASCADE,
                                related_name="participations")
    status = models.CharField(max_length=10, choices=[('absent', 'Absent'), ('present', 'Présent')], default='absent')

    def __str__(self):
        return f"Le participant {self.participant.username} a le n° {self.number_verify} pour cette réunion"

    class Meta:
        verbose_name = _("Participation")
        verbose_name_plural = _("Participations")


class MeetingReview(TimeStampedModel):
    full_name = models.CharField(max_length=150, verbose_name="Nom complet")
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name="reviews",
                                verbose_name=_("Réunion"))
    review = models.TextField(verbose_name=_('Commentaire'))

    class Meta:
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis sur les réunions")

    def __str__(self):
        return self.meeting.title


class Wishlist(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Personnel")
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, related_name="wishlists",
                                verbose_name="Réunion")

    class Meta:
        verbose_name_plural = "Liste de favoris"

    def __str__(self):
        return self.meeting.title
