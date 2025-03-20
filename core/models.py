from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model 
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('entrepreneur', 'Entrepreneur'),
        ('investisseur', 'Investisseur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    kyc_validated = models.BooleanField(default=False)  # Validation KYC
    kyc_document = models.ImageField(upload_to='kyc_documents/', blank=True, null=True)  # Upload de la carte d'identité

    REQUIRED_FIELDS = ['email']  # Supprimé 'role' et 'phone_number' pour les superutilisateurs

    def is_entrepreneur(self):
        return self.role == "entrepreneur"

    def is_investisseur(self):
        return self.role == "investisseur"

    def __str__(self):
        return f"{self.username} ({self.role if self.role else 'Superutilisateur'})"
    
    def is_kyc_pending(self):
        return self.kyc_document and not self.kyc_validated
    

User = get_user_model()

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Technologie'),
        ('health', 'Santé'),
        ('agriculture', 'Agriculture'),
        ('education', 'Éducation'),
        ('other', 'Autre'),
    ]

    entrepreneur = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'entrepreneur'})
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='projects/images/', blank=True, null=True)
    description = models.TextField()
    objectives = models.TextField()
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Somme déjà collectée
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    document = models.FileField(upload_to='media/projects/docs/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Validation par un modérateur
    created_at = models.DateTimeField(auto_now_add=True)

    def amount_collected(self):
        total = self.investment_set.aggregate(total_invested=Sum('amount'))['total_invested']
        return total if total else 0  # Si aucun investissement, retourne 0
    
    #bar de progression
    def progress_percentage(self):
        if self.amount_needed > 0:
            return min((self.amount_collected() / self.amount_needed) * 100, 100)  # Évite de dépasser 100%
        return 0


    def __str__(self):
        return self.name 
    
class Investment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    date_invested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.username} a investi {self.amount} FCFA dans {self.project.name}"


class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')  
        ordering = ['-created_at']  # Les avis les plus récents en premier

    class Meta:
        unique_together = ('project', 'user')  # Un utilisateur ne peut donner qu'une note par projet

    def __str__(self):
        return f"{self.user.username} - {self.stars}⭐ - {self.project.name}"