from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),  # Start with landing page
    path('guidelines/', views.guidelines, name='guidelines'),
    path('nationality/', views.nationality, name='nationality'),
    path('home/', views.home, name='home'),  # HomePage after nationality selection
    
    # New Registration System
    path('register/', views.user_register, name='user_register'),
    path('register-submit/', views.user_register_submit, name='user_register_submit'),
    path('send-otp/', views.send_otp_page, name='send_otp_page'),
    path('send-otp-api/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('registration-success/', views.registration_success, name='registration_success'),
    
    # New Login System
    path('login/', views.login_page, name='login_page'),
    path('login-send-otp/', views.login_send_otp, name='login_send_otp'),
    path('login-verify-otp/', views.login_verify_otp, name='login_verify_otp'),
    
    # Legacy routes (can be removed later)
    path('digilocker-login/', views.user_register, name='digilocker_login'),  # Redirect to register
    path('digilocker-signup/', views.user_register, name='digilocker_signup'),  # Redirect to register
    path('digilocker-auth/', views.user_register_submit, name='digilocker_auth'),  # Redirect to register
    path('digilocker-signup-auth/', views.user_register_submit, name='digilocker_signup_auth'),  # Redirect to register
    
    path('voter-login/', views.voter_login, name='voter_login'),
    path('voter-auth/', views.voter_auth, name='voter_auth'),
    path('voter-info/', views.voter_info, name='voter_info'),
    path('vote/', views.vote_page, name='vote'),
    path('vote', views.submit_vote, name='submit_vote'),  # For the original JS fetch call
    path('logout/', views.logout_user, name='logout'),
    path('search/', views.search_page, name='search'),
    path('nri-login/', views.nri_login, name='nri_login'),
    path('face-detection/', views.face_detection, name='face_detection'),
    
    # ============================================================
    # FEDERATED LEARNING API ENDPOINTS
    # Privacy-Preserving Biometric Authentication
    # ============================================================
    
    # Import federated views
]

# Import federated views separately to avoid circular import
from . import views_federated

# Add federated API endpoints
urlpatterns += [
    # Biometric Registration & Verification
    path('api/register-biometric/', views_federated.register_biometric_api, name='register_biometric_api'),
    path('api/verify-biometric/', views_federated.verify_biometric_api, name='verify_biometric_api'),
    
    # Federated Learning Coordination
    path('api/federated-model-info/', views_federated.federated_model_info_api, name='federated_model_info'),
    path('api/federated-gradients/', views_federated.submit_federated_gradients_api, name='submit_graderated_gradients'),
    
    # User Management
    path('api/biometric-status/', views_federated.get_user_biometric_status, name='biometric_status'),
    path('api/delete-biometric/', views_federated.delete_biometric_data, name='delete_biometric'),
    
    # Public Statistics (no personal data)
    path('api/federated-stats/', views_federated.federated_learning_stats, name='federated_stats'),
]
