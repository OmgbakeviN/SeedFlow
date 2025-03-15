from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Investment
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'kyc_validated', 'is_staff', 'is_superuser')
    list_filter = ('role', 'kyc_validated', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    actions = ['approve_kyc', 'reject_kyc']

    def approve_kyc(self, request, queryset):
        """ Valide le KYC des utilisateurs sélectionnés. """
        queryset.update(kyc_validated=True)
        self.message_user(request, "KYC approuvé avec succès.")
    approve_kyc.short_description = "Approuver le KYC"

    def reject_kyc(self, request, queryset):
        """ Rejette le KYC et force l'utilisateur à resoumettre. """
        queryset.update(kyc_validated=False, kyc_document=None)
        self.message_user(request, "KYC rejeté, l'utilisateur doit soumettre un nouveau document.")
    reject_kyc.short_description = "Rejeter le KYC"

admin.site.register(User, CustomUserAdmin)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'entrepreneur', 'category', 'amount_needed', 'is_approved', 'created_at')
    list_filter = ('category', 'is_approved')
    search_fields = ('name', 'entrepreneur__username')
    actions = ['approve_projects', 'reject_projects']

    def approve_projects(self, request, queryset):
        """ Approuve les projets sélectionnés """
        queryset.update(is_approved=True)
        self.message_user(request, "Projets approuvés avec succès.")
    approve_projects.short_description = "Approuver les projets"

    def reject_projects(self, request, queryset):
        """ Rejette les projets sélectionnés """
        queryset.update(is_approved=False)
        self.message_user(request, "Projets rejetés.")
    reject_projects.short_description = "Rejeter les projets"

admin.site.register(Project, ProjectAdmin)
admin.site.register(Investment)