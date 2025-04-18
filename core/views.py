from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Investment, Investment, Rating
from .forms import ProjectForm, SignupForm, KYCUploadForm ,ProfilePictureForm, UpdateProfileForm, InvestmentForm, UpdateUsernameForm, UpdateProfilePictureForm, RatingForm
from core.models import Project, Rating
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden, JsonResponse
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





from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.conf import settings
from pymesomb.operations import PaymentOperation
import uuid
from requests.exceptions import Timeout
from decimal import Decimal

# def investment(request, project_id):
#     project = get_object_or_404(Project, id=project_id)
#     form = InvestmentForm(request.POST or None)

#     if request.method == 'POST':
#         form = InvestmentForm(request.POST)
#         if form.is_valid():
#             amount = float(form.cleaned_data['amount'])
#             service = form.cleaned_data['service']
#             payer = form.cleaned_data['phone_number']

#             operation = PaymentOperation(
#                 settings.MESOMB_APP_KEY,
#                 settings.MESOMB_ACCESS_KEY,
#                 settings.MESOMB_SECRET_KEY
#             )

#             try:
#                 response = operation.make_collect(
#                     amount=amount,
#                     service=service,
#                     payer=payer,
#                 )

#                 print("📌 MeSomb Response:", response)

#                 if response.is_operation_success() and response.is_transaction_success():
#                     payment_status = "success"
#                     success_message = "✅ Payment successful!"
#                 else:
#                     payment_status = "failed"
#                     success_message = "❌ Payment failed. Try again."

#                 transaction = Investment.objects.create(
#                     project=project,
#                     amount=amount,
#                     service=service,
#                     payer=payer,
#                     status=payment_status,
#                     transaction_id=str(uuid.uuid4()),
#                     investor=request.user
#                 )
#                 print(f"📌 Transaction Saved - Status: {payment_status}, ID: {transaction}")

#                 if payment_status == "success":
#                     project.amount_collected += amount
#                     project.save(update_fields=['amount_collected'])
#                     print("✅ Project Updated - Amount Collected:", project.amount_collected)

#                 messages.success(request, success_message)
#                 return redirect('project_detail', project_id=project_id)

#             except Timeout:
#                 print("⏱ Payment timed out after 2 minutes.")
#                 Investment.objects.create(
#                     project=project,
#                     amount=amount,
#                     service=service,
#                     payer=payer,
#                     status="Failed",
#                     transaction_id=str(uuid.uuid4()),
#                     investor=request.user
#                 )
#                 messages.error(request, "❌ Payment failed: Timeout after 2 minutes.")
#                 return render(request, 'investment.html', {'project': project, 'form': form})

#             except Exception as e:
#                 print("❌ Payment Error:", str(e))
#                 Investment.objects.create(
#                     project=project,
#                     amount=amount,
#                     service=service,
#                     payer=payer,
#                     status="Failed",
#                     transaction_id=str(uuid.uuid4()),
#                     investor=request.user
#                 )
#                 print(f"⚠️ Transaction Saved with Error - ID: {transaction}")
#                 messages.error(request, f"❌ Payment Error: {str(e)}")
#                 return render(request, 'investment.html', {'project': project, 'form': form})

#     return render(request, 'investment.html', {'project': project, 'form': form})

def investment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    form = InvestmentForm(request.POST or None)

    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            amount = Decimal(form.cleaned_data['amount'])
            service = form.cleaned_data['service']
            payer = form.cleaned_data['phone_number']

            operation = PaymentOperation(
                settings.MESOMB_APP_KEY,
                settings.MESOMB_ACCESS_KEY,
                settings.MESOMB_SECRET_KEY
            )

            try:
                response = operation.make_collect(
                    amount=amount,
                    service=service,
                    payer=payer,
                )

                print("📌 MeSomb Response:", response)

                # ✅ STRICT success check
                if response.is_operation_success() and response.is_transaction_success():
                    # Create only if payment succeeded
                    Investment.objects.create(
                        project=project,
                        amount=amount,
                        service=service,
                        payer=payer,
                        status='success',
                        transaction_id=str(uuid.uuid4()),
                        investor=request.user
                    )

                    project.amount_collected += amount
                    project.save(update_fields=['amount_collected'])

                    print("✅ Project Updated - Amount Collected:", project.amount_collected)
                    messages.success(request, "✅ Payment successful!")
                    return redirect('project_detail', project_id=project_id)

                else:
                    # ❌ Payment failed, do NOT create an Investment record
                    print("❌ Payment failed. Transaction NOT saved.")
                    messages.error(request, "❌ Payment failed. Try again.")
                    return render(request, 'investment.html', {'project': project, 'form': form})

            except Timeout:
                print("⏱ Payment timed out after 2 minutes.")
                messages.error(request, "❌ Payment failed: Timeout after 2 minutes.")
                return render(request, 'investment.html', {'project': project, 'form': form})

            except Exception as e:
                print("❌ Payment Error:", str(e))
                messages.error(request, f"❌ Payment Error: {str(e)}")
                return render(request, 'investment.html', {'project': project, 'form': form})

    return render(request, 'investment.html', {'project': project, 'form': form})






@login_required
@kyc_required
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    rating, created = Rating.objects.get_or_create(user=request.user, project=project)
    
    if rating.liked:
        rating.liked = False
    else:
        rating.liked = True
    rating.save()
    
    return JsonResponse({'likes_count': project.rating_set.filter(liked=True).count()})

@login_required
@kyc_required
def rate_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    rating_instance = Rating.objects.filter(project=project, user=request.user).first()

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating_instance)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.project = project
            rating.user = request.user
            rating.save()
            messages.success(request, "Votre note a été enregistrée avec succès !")
            return redirect('project_detail', project_id=project.id)
    else:
        form = RatingForm(instance=rating_instance)

    return render(request, 'rate_project.html', {'form': form, 'project': project})


