from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=150, verbose_name="Nom d'utilisateur")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    bio = models.CharField(max_length=1000, verbose_name="Biographie")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.username}"
    

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    image = models.ImageField(upload_to="image", default='default.png')
    full_name = models.CharField(max_length=200, verbose_name = "Nom complet")
    phone = models.CharField(max_length=200, verbose_name = "Téléphone")
    fonction =  models.CharField(max_length=150, verbose_name="Fonction", default="personnel")
    role = models.CharField(max_length=100, verbose_name="Rôle")
    verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Profil"

    def __str__(self):
        return self.user.username
  
    

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
