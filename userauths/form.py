from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile

class UserRegisterForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'maxlength':10, 'class':'form-control'}),
                             error_messages={'required': 'Veuillez entrer un nom d\'utilisateur.', 'class':'form-control'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'E-mail', 'class':'form-control'}),
                           error_messages={'required': 'Veuillez entrer une adresse e-mail valide.'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class':'form-control'}),
                              error_messages={'required': 'Veuillez entrer un mot de passe.'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirmation du mot de passe', 'class':'form-control'}),
                              error_messages={'required': 'Veuillez entrer une confirmation du mot de passe.'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    

class ProfileForm(forms.ModelForm):
    
    full_name=forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nom complet...",}),
                             error_messages={'required': 'Veuillez entrer votre nom complet.'})
    bio=forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Biographie...",}),
                            error_messages={'required': 'Veuillez entrer votre biograhie.'})
    
    phone=forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Téléphone...",}),
                            error_messages={'required': 'Veuillez entrer votre numéro de téléphone.'})

    class Meta:
        model = Profile
        fields = ['image', 'full_name', 'bio', 'phone']  