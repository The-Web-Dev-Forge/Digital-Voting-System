from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class RegisteredUser(models.Model):
    """Model for user registration with comprehensive voter information"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    RELATION_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('husband', 'Husband'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200, help_text="Full name as per government ID")
    username = models.CharField(max_length=100, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Government IDs
    voter_id_epic = models.CharField(max_length=20, unique=True, help_text="Voter ID EPIC number")
    aadhaar_number = models.CharField(max_length=12, unique=True, help_text="Aadhar card number")
    
    # Family Information
    guardian_name = models.CharField(max_length=200, help_text="Father/Mother/Husband name as per voter ID")
    guardian_relation = models.CharField(max_length=10, choices=RELATION_CHOICES)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, unique=True, help_text="Registered phone number")
    email = models.EmailField(blank=True, null=True, help_text="Email address (optional)")
    
    # Address Information
    address = models.TextField(help_text="Voter's complete address")
    constituency = models.CharField(max_length=200, help_text="Voting constituency")
    
    # Document Uploads
    aadhaar_image = models.ImageField(upload_to='user_documents/aadhaar/', help_text="Upload Aadhar card image")
    voter_id_image = models.ImageField(upload_to='user_documents/voter_id/', help_text="Upload Voter ID image")
    
    # Verification Status
    phone_verified = models.BooleanField(default=False)
    documents_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to actual voter record if approved
    linked_voter = models.OneToOneField('Voter', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.voter_id_epic}"
    
    class Meta:
        verbose_name = "Registered User"
        verbose_name_plural = "Registered Users"

class Party(models.Model):
    name = models.CharField(max_length=200)
    symbol = models.ImageField(upload_to='party_symbols/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Parties"

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='candidate_photos/')
    constituency = models.CharField(max_length=200, default='Default Constituency')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.party.name}"

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    voter_id = models.CharField(max_length=20, unique=True)
    constituency = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.voter_id}"

class Vote(models.Model):
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Vote by {self.voter.voter_id} for {self.candidate.name}"
    
    class Meta:
        unique_together = ['voter', 'candidate']

class LoginSession(models.Model):
    LOGIN_TYPES = [
        ('digilocker', 'Digilocker'),
        ('voter_id', 'Voter ID'),
    ]
    
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    login_type = models.CharField(max_length=20, choices=LOGIN_TYPES)
    session_key = models.CharField(max_length=200)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.voter.voter_id} - {self.login_type} - {self.login_time}"

class OTP(models.Model):
    """Model to store OTP for phone verification"""
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)  # 5 minutes expiry
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.otp_code}"
    
    class Meta:
        ordering = ['-created_at']


# ============================================================
# FEDERATED LEARNING MODELS
# Import from federated_auth.py to maintain separation of concerns
# ============================================================

from .federated_auth import (
    BiometricEmbedding,
    FederatedModelVersion,
    FederatedGradientContribution,
    BiometricAuthLog,
    FederatedAuthenticationManager
)
