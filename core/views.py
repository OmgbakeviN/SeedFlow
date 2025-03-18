from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Investment, Investment
from .forms import ProjectForm, SignupForm, KYCUploadForm ,ProfilePictureForm, UpdateProfileForm, InvestmentForm, UpdateUsernameForm, UpdateProfilePictureForm
from core.models import Project
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
import requests
import os
import hashlib
import hmac
import base64

# Create your views here.

def kyc_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.kyc_validated:
            return redirect("kyc_pending")
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@kyc_required
def dashboard_entrepreneur(request):
    if not request.user.kyc_validated:
        return redirect('kyc_pending')  # Rediriger vers une page d'attente
    return render(request, 'dashboard_entrepreneur.html')

@login_required
@kyc_required
def submit_project(request):
    if request.user.role != 'entrepreneur' or not request.user.kyc_validated:
        return redirect('dashboard')  # Rediriger si non éligible

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.entrepreneur = request.user
            project.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    
    return render(request, 'submit_project.html', {'form': form})

@login_required
@kyc_required
def project_list(request):
    projects = Project.objects.filter(is_approved=True)
    return render(request, 'project_list.html', {'projects': projects})

def home(request):
    projects = Project.objects.filter(is_approved=True)  # Récupère seulement les projets validés
    return render(request, 'project_list.html', {'projects': projects})

from django.shortcuts import render, get_object_or_404
from .models import Project

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'core/project_detail.html', {'project': project})

def project_list(request):
    projects = Project.objects.filter(is_approved=True)  # Afficher uniquement les projets validés
    return render(request, 'project_list.html', {'projects': projects})

@login_required
@kyc_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.entrepreneur = request.user  # Associer le projet à l'utilisateur connecté
            project.is_approved = False  # Le projet doit être validé avant d'apparaître
            project.save()
            return redirect('projects')  # Rediriger vers la liste des projets après soumission
    else:
        form = ProjectForm()
    
    return render(request, 'create_project.html', {'form': form})

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_detail.html', {'project': project})

@login_required
@kyc_required
def entrepreneur_dashboard(request):
    projects = Project.objects.filter(entrepreneur=request.user)  # Projets de l'entrepreneur connecté
    return render(request, 'entrepreneur_dashboard.html', {'projects': projects})

@login_required
@kyc_required
def investor_dashboard(request):
    investments = Investment.objects.filter(investor=request.user)
    return render(request, "investor_dashboard.html", {"investments": investments})

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Vérifier le rôle de l'utilisateur et rediriger
            if user.role == "Entrepreneur":
                return redirect("entrepreneur_dashboard")
            elif user.role == "Investisseur":
                return redirect("investor_dashboard")
            else:
                return redirect("/")  # Page d'accueil ou une autre page par défaut
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après inscription

            # Redirection vers la soumission KYC si ce n'est pas encore validé
            if not user.kyc_validated:
                return redirect("upload_kyc")  # Nom de l'URL pour l'envoi KYC
            
            # Si KYC déjà validé, on redirige normalement
            if user.role == "Entrepreneur":
                return redirect("entrepreneur_dashboard")
            elif user.role == "Investisseur":
                return redirect("investor_dashboard")
            else:
                return redirect("/")
    else:
        form = SignupForm()
    
    return render(request, "signup.html", {"form": form})

@login_required
def upload_kyc(request):
    if request.user.kyc_validated:
        if request.user.role == "Entrepreneur":
            return redirect("entrepreneur_dashboard")
        elif request.user.role == "Investisseur":
            return redirect("investor_dashboard")
        else:
            return redirect("home")  # Ou une autre page par défaut

    if request.method == "POST":
        form = KYCUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("kyc_pending")
    else:
        form = KYCUploadForm()

    return render(request, "kyc_upload.html", {"form": form})

@login_required
def kyc_pending(request):
    if request.user.kyc_validated:
        if request.user.role == "Entrepreneur":
            return redirect("entrepreneur_dashboard")
        elif request.user.role == "Investisseur":
            return redirect("investor_dashboard")
        else:
            return redirect("home")  # Ou une autre page par défaut

    return render(request, "kyc_pending.html")


def logout_view(request):
    logout(request)
    return redirect("login")  # Redirige vers la page de connexion après déconnexion



@login_required
def update_profile(request):
    if request.method == "POST":
        if "update_username" in request.POST:  # Si l'utilisateur modifie son nom
            username_form = UpdateUsernameForm(request.POST, instance=request.user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Nom d'utilisateur mis à jour avec succès.")
                return redirect("update_profile")

        elif "update_profile_picture" in request.POST:  # Si l'utilisateur met à jour sa photo
            picture_form = UpdateProfilePictureForm(request.POST, request.FILES, instance=request.user)
            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, "Photo de profil mise à jour avec succès.")
                return redirect("update_profile")

    else:
        username_form = UpdateUsernameForm(instance=request.user)
        picture_form = UpdateProfilePictureForm(instance=request.user)

    return render(request, "update_profile.html", {
        "username_form": username_form,
        "picture_form": picture_form
    })




# APPLICATION_KEY = settings.MESOMB_APPLICATION_KEY
# ACCESS_KEY = settings.MESOMB_ACCESS_KEY
# SECRET_KEY = settings.MESOMB_SECRET_KEY

# MESOMB_URL = "https://mesomb.hachther.com/api/v1.1/payment/collect/"

# import time

# # def generate_mesomb_signature(data):
# #     """Generate HMAC signature for MeSomb request"""
# #     timestamp = str(int(time.time()))
# #     message = f"{ACCESS_KEY}:{data['amount']}:{data['payer']}:{data['service']}:{data['country']}"
# #     signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha1).digest()
# #     return base64.b64encode(signature).decode(), timestamp

# def generate_mesomb_signature(data):
#     """Generate a valid HMAC signature for MeSomb"""
#     timestamp = str(int(time.time()))  # Ensure timestamp is an integer string

#     # Ensure all fields are in the correct order
#     elements = [
#         ACCESS_KEY,
#         timestamp,
#         str(data["amount"]),  # Convert to string
#         data["payer"],
#         data["service"],
#         data["country"],
#     ]
    
#     message = ":".join(elements)  # Join elements with a colon (:)

#     # Generate HMAC-SHA1 signature
#     signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha1).digest()
#     signature_b64 = base64.b64encode(signature).decode() 
#     return signature_b64, timestamp  # Return signature & timestamp

# @login_required
# @kyc_required
# def investment(request, project_id):
#     project = get_object_or_404 (Project,id=project_id)
    
#     if request.method == "POST":
#         form = InvestmentForm(request.POST)
#         if form.is_valid():
#             amount = form.cleaned_data['amount']
#             phone_number = form.cleaned_data['phone_number']
#             service = form.cleaned_data['service']
            
#             timestamp = str(int(time.time()))
#             data = {
#                 'payer': phone_number,
#                 'amount': amount,
#                 'fees': True,
#                 'service': service,
#                 'currency': 'XAF',
#                 'message': "Project Payment",
#                 'country':'CM'
#             }

#             signature, timestamp = generate_mesomb_signature(data)

#             headers = {
#                 "X-MeSomb-Application": APPLICATION_KEY,
#                 "X-MeSomb-AccessKey": ACCESS_KEY,
#                 "X-MeSomb-Signature": signature,
#                 "X-MeSomb-Timestamp": timestamp,
#                 "Content-Type": "application/json"
#             }

#             print("debug: headers being sent:", headers)
#             print("debug: payload being sent:", data)

#             # try:
#             #     response = requests.post(MESOMB_URL, json=data, headers=headers)
#             #     response_data = response.json()

#             #     if response_data.get("success", False):
#             #         # Save investment if transaction is successful
#             #         investment = Investment.objects.create(
#             #             investor=request.user,
#             #             project=project,
#             #             amount=amount
#             #         )
#             #         investment.save()

#             #         messages.success(request, f"Votre investissement de {amount} FCFA a été effectué avec succès!")
#             #         return redirect('project_detail', project_id=project.id)
#             #     else:
#             #         messages.error(request, f"Échec du paiement: {response_data.get('message', 'Erreur inconnue')}")
            
#             # except requests.exceptions.RequestException as e:
#             #     messages.error(request, f"Erreur de connexion: {str(e)}")


#             try:
#                 response = requests.post(MESOMB_URL, json=data, headers=headers)
#                 response_data = response.json()

#                 print("DEBUG: MeSomb Response:", response_data)  # Add this line

#                 if response_data.get("success", False):
#                     # Save investment if transaction is successful
#                     investment = Investment.objects.create(
#                         investor=request.user,
#                         project=project,
#                         amount=amount
#                     )
#                     investment.save()

#                     messages.success(request, f"Votre paiement de {amount} FCFA a été collecté avec succès!")
#                     return redirect('project_detail', project_id=project.id)
#                 else:
#                     error_message = response_data.get("message", "Erreur inconnue")  # Extract error message
#                     messages.error(request, f"Échec du paiement: {error_message}")

#             except requests.exceptions.RequestException as e:
#                 messages.error(request, f"Erreur de connexion: {str(e)}")

#     else:
#         form = InvestmentForm()

#     return render(request, 'investment.html', {'form': form, 'project': project})



import requests
from django.conf import settings  # Import Django settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Investment, Project
from .forms import InvestmentForm

# Load API keys from Django settings
APPLICATION_KEY = settings.MESOMB_APPLICATION_KEY

MESOMB_URL = "https://mesomb.hachther.com/api/v1.1/payment/online/"  # Matches PHP script

@login_required
def investment(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            phone_number = form.cleaned_data['phone_number']
            service = form.cleaned_data['service']

            # Prepare request payload
            data = {
                "payer": phone_number,
                "amount": amount,
                "fees": True,
                "service": service,
                "currency": "XAF",
                "message": "Project Payment",
                "country": "CM"
            }

            # Headers (No signature needed)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla",
                "X-MeSomb-Application": APPLICATION_KEY  # Only Application Key needed
            }

            # Debugging print
            print("DEBUG: Headers being sent:", headers)
            print("DEBUG: Payload being sent:", data)

            # Send request to MeSomb
            try:
                response = requests.post(MESOMB_URL, json=data, headers=headers)

                # Debugging print: raw response
                print("DEBUG: Raw MeSomb Response:", response.text)

                # Handle empty response
                try:
                    response_data = response.json()
                except ValueError:
                    print("DEBUG: Empty or invalid JSON response from MeSomb")  # Debugging
                    messages.error(request, "Erreur de connexion: Réponse invalide de MeSomb")
                    return redirect('project_detail', project_id=project.id)

                # Debugging print: parsed JSON response
                print("DEBUG: Parsed MeSomb Response:", response_data)

                if response.status_code == 200 and response_data.get("success", False):
                    # Save investment if transaction is successful
                    investment = Investment.objects.create(
                        investor=request.user,
                        project=project,
                        amount=amount
                    )
                    investment.save()

                    messages.success(request, f"Votre paiement de {amount} FCFA a été collecté avec succès!")
                    return redirect('project_detail', project_id=project.id)
                else:
                    error_message = response_data.get("message", "Erreur inconnue")
                    messages.error(request, f"Échec du paiement: {error_message}")

            except requests.exceptions.RequestException as e:
                print("DEBUG: Connection Error:", str(e))  # Debugging
                messages.error(request, f"Erreur de connexion: {str(e)}")

    else:
        form = InvestmentForm()

    return render(request, 'investment.html', {'form': form, 'project': project})