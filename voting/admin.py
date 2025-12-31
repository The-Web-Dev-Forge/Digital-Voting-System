from django.contrib import admin
from .models import Party, Candidate, Voter, Vote, LoginSession, RegisteredUser, OTP

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'username', 'voter_id_epic', 'phone_number', 'phone_verified', 'documents_verified', 'is_approved', 'created_at']
    search_fields = ['full_name', 'username', 'voter_id_epic', 'aadhaar_number', 'phone_number']
    list_filter = ['gender', 'guardian_relation', 'phone_verified', 'documents_verified', 'is_approved', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['linked_voter']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'username', 'date_of_birth', 'gender')
        }),
        ('Government IDs', {
            'fields': ('voter_id_epic', 'aadhaar_number')
        }),
        ('Family Information', {
            'fields': ('guardian_name', 'guardian_relation')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Address Information', {
            'fields': ('address', 'constituency')
        }),
        ('Document Uploads', {
            'fields': ('aadhaar_image', 'voter_id_image')
        }),
        ('Verification Status', {
            'fields': ('phone_verified', 'documents_verified', 'is_approved')
        }),
        ('Voter Linking', {
            'fields': ('linked_voter',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    actions = ['approve_registration', 'mark_documents_verified']
    
    def approve_registration(self, request, queryset):
        updated = queryset.update(is_approved=True, documents_verified=True)
        self.message_user(request, f'{updated} registrations approved successfully.')
    approve_registration.short_description = "Approve selected registrations"
    
    def mark_documents_verified(self, request, queryset):
        updated = queryset.update(documents_verified=True)
        self.message_user(request, f'{updated} documents marked as verified.')
    mark_documents_verified.short_description = "Mark documents as verified"

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'created_at', 'expires_at', 'is_verified', 'is_used']
    search_fields = ['phone_number']
    list_filter = ['is_verified', 'is_used', 'created_at']
    readonly_fields = ['created_at', 'expires_at']
    
    def has_add_permission(self, request):
        return False  # Prevent manual OTP creation

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'constituency', 'created_at']
    search_fields = ['name', 'party__name', 'constituency']
    list_filter = ['party', 'constituency', 'created_at']
    list_select_related = ['party']

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['user', 'voter_id', 'constituency', 'has_voted', 'created_at']
    search_fields = ['user__username', 'voter_id', 'constituency']
    list_filter = ['constituency', 'has_voted', 'created_at']
    readonly_fields = ['created_at']
    list_select_related = ['user']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'timestamp', 'ip_address']
    search_fields = ['voter__voter_id', 'candidate__name']
    list_filter = ['candidate__party', 'timestamp']
    readonly_fields = ['timestamp']
    list_select_related = ['voter', 'candidate', 'candidate__party']
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent vote modification
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent vote deletion

@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ['voter', 'login_type', 'login_time', 'logout_time', 'is_active']
    search_fields = ['voter__voter_id']
    list_filter = ['login_type', 'is_active', 'login_time']
    readonly_fields = ['login_time', 'logout_time']
    list_select_related = ['voter']
