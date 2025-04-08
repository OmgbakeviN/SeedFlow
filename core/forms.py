from django import forms
from .models import Project, User, Investment, Rating
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'objectives', 'amount_needed', 'category', 'document', 'image']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['objectives'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['amount_needed'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['document'].widget.attrs.update({'class': 'form-control'})

class SignupForm(UserCreationForm):
    username = forms.CharField(
        max_length=150, 
        required=True, 
        help_text="Obligatoire. 150 caractères max.",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Nom d'utilisateur"
        })
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={  # Changé de TextInput à FileInput pour les fichiers
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        })
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Prénom"
        })
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Nom"
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "email@exemple.com"
        })
    )
    
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "77 123 45 67"
        })
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,  # Supposant que vous avez défini ROLE_CHOICES dans votre modèle User
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Mot de passe"
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 mt-1 text-gray-700 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Confirmation du mot de passe"
        })
    )
    
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number", "role", "profile_picture", "password1", "password2"]
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return phone_number
    
class KYCUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['kyc_document']

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']

class UpdateProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput,
        required=False,  # Rendre le mot de passe optionnel
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = ["profile_picture", "username"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)

        if commit:
            user.save()
        
        return user
    
class InvestmentForm(forms.Form):
    amount = forms.IntegerField(
        min_value= 10000, 
        label= "entrez un montant plus grand que 10000FCFA",
        widget=forms.NumberInput(attrs={"class":"form-control", "placeholder":"entrez le montant"})
    )
    phone_number = forms.CharField(
        max_length=15, 
        label= "entrez un numero d telephone",
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"entrez le numero de telephone"})
    )
    
    SERVICE_CHOICES=[
        ("MTN","MTN"),
        ("ORANGE","ORANGE"),
    ]

    service = forms.ChoiceField( 
        choices=SERVICE_CHOICES,
        label= "service",
        widget=forms.Select(attrs={"class":"form-control"})
    )

class UpdateUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]

class UpdateProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile_picture"]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.Select(choices=[(i, f"{i} ⭐") for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Laissez un commentaire...'}),
        }