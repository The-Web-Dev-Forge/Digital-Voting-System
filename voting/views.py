from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
import json
import logging
import random
from datetime import datetime

from .models import Voter, Candidate, Party, Vote, LoginSession, RegisteredUser, OTP

logger = logging.getLogger(__name__)

def home(request):
    """Homepage with login options"""
    return render(request, 'voting/home.html')

def landing(request):
    """Landing page for new users"""
    return render(request, 'voting/landing.html')

def guidelines(request):
    """Guidelines page"""
    return render(request, 'voting/guidelines.html')

def nationality(request):
    """Nationality selection page"""
    return render(request, 'voting/nationality.html')

def user_register(request):
    """User registration page"""
    return render(request, 'voting/user_register.html')

@csrf_exempt
def user_register_submit(request):
    """Handle user registration form submission"""
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.POST.get('full_name', '').strip()
            username = request.POST.get('username', '').strip()
            date_of_birth = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            voter_id_epic = request.POST.get('voter_id_epic', '').strip()
            aadhaar_number = request.POST.get('aadhaar_number', '').strip()
            guardian_name = request.POST.get('guardian_name', '').strip()
            guardian_relation = request.POST.get('guardian_relation')
            phone_number = request.POST.get('phone_number', '').strip()
            email = request.POST.get('email', '').strip()
            address = request.POST.get('address', '').strip()
            constituency = request.POST.get('constituency', '').strip()
            aadhaar_image = request.FILES.get('aadhaar_image')
            voter_id_image = request.FILES.get('voter_id_image')
            
            # Validation with detailed error messages
            missing_fields = []
            if not full_name:
                missing_fields.append('Full Name')
            if not username:
                missing_fields.append('Username')
            if not date_of_birth:
                missing_fields.append('Date of Birth')
            if not gender:
                missing_fields.append('Gender')
            if not voter_id_epic:
                missing_fields.append('Voter ID EPIC Number')
            if not aadhaar_number:
                missing_fields.append('Aadhaar Number')
            if not guardian_name:
                missing_fields.append("Guardian's Name")
            if not guardian_relation:
                missing_fields.append('Guardian Relation')
            if not phone_number:
                missing_fields.append('Phone Number')
            if not address:
                missing_fields.append('Address')
            if not constituency:
                missing_fields.append('Constituency')
            if not aadhaar_image:
                missing_fields.append('Aadhaar Image')
            if not voter_id_image:
                missing_fields.append('Voter ID Image')
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'message': f"Missing required fields: {', '.join(missing_fields)}"
                })
            
            # Check if username, voter ID, or Aadhaar already exists
            if RegisteredUser.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Username already exists'
                })
            
            if RegisteredUser.objects.filter(voter_id_epic=voter_id_epic).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Voter ID already registered'
                })
            
            if RegisteredUser.objects.filter(aadhaar_number=aadhaar_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Aadhaar number already registered'
                })
            
            if RegisteredUser.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Phone number already registered'
                })
            
            # Validate Aadhaar number (12 digits)
            if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
                return JsonResponse({
                    'success': False,
                    'message': 'Aadhaar number must be 12 digits'
                })
            
            # Validate phone number (10 digits)
            if not phone_number.isdigit() or len(phone_number) != 10:
                return JsonResponse({
                    'success': False,
                    'message': 'Phone number must be 10 digits'
                })
            
            # Create user registration
            with transaction.atomic():
                user_registration = RegisteredUser.objects.create(
                    full_name=full_name,
                    username=username,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    voter_id_epic=voter_id_epic,
                    aadhaar_number=aadhaar_number,
                    guardian_name=guardian_name,
                    guardian_relation=guardian_relation,
                    phone_number=phone_number,
                    email=email if email else None,
                    address=address,
                    constituency=constituency,
                    aadhaar_image=aadhaar_image,
                    voter_id_image=voter_id_image
                )
                
                # Store user registration ID in session for OTP verification
                request.session['pending_registration_id'] = user_registration.id
                
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful! Please verify your phone number.',
                    'redirect_url': '/send-otp/'
                })
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Registration failed. Please try again.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def voter_login(request):
    """Voter ID login page"""
    return render(request, 'voting/voter_login.html')

@csrf_exempt
def voter_auth(request):
    """Handle Voter ID authentication with OTP verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voter_id = data.get('voter_id')
            phone = data.get('phone')
            otp = data.get('otp')
            
            # Validate required fields
            if not voter_id or not phone:
                return JsonResponse({'error': 'Voter ID and phone number are required'}, status=400)
            
            # If OTP is provided, verify it (simplified - accept any 6-digit OTP)
            if otp:
                # Simple validation - just check if it's 6 digits
                if not otp.isdigit() or len(otp) != 6:
                    return JsonResponse({'error': 'Please enter a valid 6-digit OTP'}, status=400)
                
                # For development/testing - accept any 6-digit OTP
                # In production, you would implement proper SMS OTP verification here
                logger.info(f"OTP verification bypassed for development - accepted OTP: {otp} for phone: {phone}")
            
            # Check if voter exists
            try:
                voter = Voter.objects.get(voter_id=voter_id)
                if voter.has_voted:
                    return JsonResponse({'error': 'You have already voted'}, status=400)
                
                # Verify phone number matches (for security)
                if voter.phone_number and voter.phone_number != phone:
                    return JsonResponse({'error': 'Phone number does not match our records'}, status=400)
                
                # Create login session
                session = LoginSession.objects.create(
                    voter=voter,
                    login_type='voter_id',
                    session_key=request.session.session_key or '',
                )
                
                # Store user details in session
                request.session['user_details'] = {
                    'voter_id': voter_id,
                    'username': voter.user.username,
                    'login_type': 'voter_id',
                    'constituency': voter.constituency
                }
                
                return JsonResponse({'success': True, 'redirect': '/voter-info/'})
                
            except Voter.DoesNotExist:
                return JsonResponse({'error': 'Voter ID not found. Please check your voter ID.'}, status=404)
                
        except Exception as e:
            logger.error(f"Voter auth error: {e}")
            return JsonResponse({'error': 'Authentication failed'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def vote_page(request):
    """Main voting page"""
    # Check if user is authenticated via session
    user_details = request.session.get('user_details')
    if not user_details:
        return redirect('home')
    
    # Get voter
    try:
        voter = Voter.objects.get(voter_id=user_details['voter_id'])
        if voter.has_voted:
            messages.error(request, 'You have already voted')
            return redirect('home')
    except Voter.DoesNotExist:
        return redirect('home')
    
    # Get candidates for the voter's constituency
    candidates = Candidate.objects.filter(constituency=voter.constituency).select_related('party')
    
    return render(request, 'voting/vote.html', {
        'candidates': candidates,
        'voter': voter
    })

@csrf_exempt
@require_http_methods(["POST"])
def submit_vote(request):
    """Handle vote submission"""
    user_details = request.session.get('user_details')
    if not user_details:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        candidate_name = data.get('candidate')
        party_name = data.get('party')
        
        with transaction.atomic():
            # Get voter
            voter = Voter.objects.get(voter_id=user_details['voter_id'])
            
            # Check if already voted
            if voter.has_voted:
                return JsonResponse({'error': 'You have already voted'}, status=400)
            
            # Get candidate
            candidate = Candidate.objects.get(name=candidate_name, party__name=party_name)
            
            # Create vote record
            vote = Vote.objects.create(
                voter=voter,
                candidate=candidate,
                ip_address=get_client_ip(request)
            )
            
            # Mark voter as having voted
            voter.has_voted = True
            voter.save()
            
            # Clear session
            request.session.flush()
            
            return JsonResponse({'success': True, 'message': 'Vote submitted successfully'})
            
    except Voter.DoesNotExist:
        return JsonResponse({'error': 'Voter not found'}, status=404)
    except Candidate.DoesNotExist:
        return JsonResponse({'error': 'Candidate not found'}, status=404)
    except Exception as e:
        logger.error(f"Vote submission error: {e}")
        return JsonResponse({'error': 'Failed to submit vote'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def logout_user(request):
    """Handle user logout"""
    user_details = request.session.get('user_details')
    if user_details:
        try:
            # Update login session
            voter = Voter.objects.get(voter_id=user_details['voter_id'])
            session = LoginSession.objects.filter(
                voter=voter, 
                is_active=True
            ).first()
            if session:
                session.logout_time = timezone.now()
                session.is_active = False
                session.save()
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    request.session.flush()
    return JsonResponse({'success': True})

def voter_info(request):
    """Voter information page"""
    user_details = request.session.get('user_details')
    if not user_details:
        return redirect('home')
    
    try:
        voter = Voter.objects.get(voter_id=user_details['voter_id'])
        # Try to get the RegisteredUser data linked to this voter
        registered_user = None
        try:
            registered_user = RegisteredUser.objects.get(linked_voter=voter)
        except RegisteredUser.DoesNotExist:
            # Fallback: try to find by voter_id_epic matching voter.voter_id
            try:
                registered_user = RegisteredUser.objects.get(voter_id_epic=voter.voter_id)
            except RegisteredUser.DoesNotExist:
                pass
        
        context = {
            'voter': voter,
            'registered_user': registered_user
        }
        return render(request, 'voting/voter_info.html', context)
    except Voter.DoesNotExist:
        return redirect('home')

def search_page(request):
    """Search functionality page"""
    return render(request, 'voting/search.html')

def nri_login(request):
    """NRI login page"""
    return render(request, 'voting/nri_login.html')

def face_detection(request):
    """Face detection page"""
    user_details = request.session.get('user_details')
    if not user_details:
        return redirect('home')
    
    try:
        voter = Voter.objects.get(voter_id=user_details['voter_id'])
        # Render the upgraded liveness verification template
        return render(request, 'voting/face_liveness.html', {
            'voter': voter,
            'user_details': user_details
        })
    except Voter.DoesNotExist:
        return redirect('home')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_otp_page(request):
    """OTP verification page"""
    pending_registration_id = request.session.get('pending_registration_id')
    if not pending_registration_id:
        messages.error(request, 'No pending registration found. Please register first.')
        return redirect('user_register')
    
    try:
        registration = RegisteredUser.objects.get(id=pending_registration_id)
        return render(request, 'voting/otp_verification.html', {
            'phone_number': registration.phone_number,
            'full_name': registration.full_name
        })
    except RegisteredUser.DoesNotExist:
        messages.error(request, 'Registration not found. Please register again.')
        return redirect('user_register')

def login_page(request):
    """Multi-method login page"""
    return render(request, 'voting/login.html')

@csrf_exempt
def login_send_otp(request):
    """Send OTP for login verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            method = data.get('method')
            phone = data.get('phone')
            
            # Validate phone number
            if not phone or len(phone) != 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide a valid 10-digit phone number'
                })
            
            # Store login attempt data in session
            request.session['login_attempt'] = {
                'method': method,
                'phone': phone,
                'data': data
            }
            
            # For development - generate and log OTP
            otp_code = str(random.randint(100000, 999999))
            logger.info(f"Login OTP for {phone}: {otp_code} (method: {method})")
            print(f"Login OTP for {phone}: {otp_code} (method: {method})")
            
            return JsonResponse({
                'success': True,
                'message': f'OTP sent successfully to {phone}',
                'otp': otp_code  # Remove this in production
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error sending login OTP: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to send OTP. Please try again.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def login_verify_otp(request):
    """Verify OTP and complete login"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            otp_code = data.get('otp', '').strip()
            
            # Get login attempt data
            login_attempt = request.session.get('login_attempt')
            if not login_attempt:
                return JsonResponse({
                    'success': False,
                    'error': 'No login attempt found. Please try again.'
                })
            
            # Validate OTP (accept any 6-digit code for development)
            if not otp_code or not otp_code.isdigit() or len(otp_code) != 6:
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter a valid 6-digit OTP'
                })
            
            # For development - accept any 6-digit OTP
            logger.info(f"Login OTP verification bypassed - accepted OTP: {otp_code} for phone: {login_attempt['phone']}")
            
            # Create mock user session for development
            # In production, you would verify the user exists in your database
            request.session['user_details'] = {
                'voter_id': 'ABC1234567',  # Mock voter ID
                'username': login_attempt['data'].get('name_input', 'Test User'),
                'login_type': login_attempt['method'],
                'constituency': 'Test Constituency',
                'phone': login_attempt['phone']
            }
            
            # Clear login attempt
            del request.session['login_attempt']
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful! Redirecting to voter information...',
                'redirect_url': '/voter-info/'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error verifying login OTP: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Verification failed. Please try again.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def send_otp(request):
    """Send OTP to phone number for verification"""
    if request.method == 'POST':
        try:
            # Check if this is for registration
            pending_registration_id = request.session.get('pending_registration_id')
            if pending_registration_id:
                try:
                    registration = RegisteredUser.objects.get(id=pending_registration_id)
                    phone = registration.phone_number
                except RegisteredUser.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Registration not found'
                    })
            else:
                # For other uses (legacy support)
                data = json.loads(request.body)
                phone = data.get('phone', '').strip()
            
            if not phone or len(phone) != 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide a valid 10-digit phone number'
                })
            
            # Generate 6-digit OTP (for display purposes only)
            otp_code = str(random.randint(100000, 999999))
            
            # Skip database operations for development
            # No need to create OTP records since we accept any 6-digit code
            
            # Here you would integrate with an SMS service like Twilio, AWS SNS, etc.
            # For development, we'll just log the OTP
            logger.info(f"OTP for {phone}: {otp_code} (development mode - any 6-digit code accepted)")
            print(f"OTP for {phone}: {otp_code} (development mode - any 6-digit code accepted)")  # Console output for development
            
            return JsonResponse({
                'success': True,
                'message': f'OTP sent successfully to {phone}',
                'otp': otp_code  # Remove this in production - only for development
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error sending OTP: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to send OTP. Please try again.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@csrf_exempt
def verify_otp(request):
    """Verify OTP and complete registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            otp_code = data.get('otp', '').strip()
            
            # Get pending registration
            pending_registration_id = request.session.get('pending_registration_id')
            if not pending_registration_id:
                return JsonResponse({
                    'success': False,
                    'error': 'No pending registration found'
                })
            
            try:
                registration = RegisteredUser.objects.get(id=pending_registration_id)
            except RegisteredUser.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Registration not found'
                })
            
            # Verify OTP - Simplified for development (accept any 6-digit code)
            if not otp_code or not otp_code.isdigit() or len(otp_code) != 6:
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter a valid 6-digit OTP'
                })
            
            # For development - accept any 6-digit OTP
            logger.info(f"OTP verification bypassed - accepted OTP: {otp_code} for phone: {registration.phone_number}")
            
            # Mark phone as verified and complete registration
            with transaction.atomic():
                registration.phone_verified = True
                
                # Auto-approve and create voter account for seamless experience
                registration.documents_verified = True
                registration.is_approved = True
                
                # Create Django User account
                django_user, created = User.objects.get_or_create(
                    username=registration.username,
                    defaults={
                        'first_name': registration.full_name.split()[0],
                        'last_name': ' '.join(registration.full_name.split()[1:]) if len(registration.full_name.split()) > 1 else '',
                        'email': registration.email or '',
                        'is_active': True,
                    }
                )
                
                if created:
                    # Set a default password (user will login via OTP)
                    django_user.set_password('temp_password_123')
                    django_user.save()
                
                # Create Voter account
                voter, voter_created = Voter.objects.get_or_create(
                    voter_id=registration.voter_id_epic,
                    defaults={
                        'user': django_user,
                        'constituency': registration.constituency,
                        'phone_number': registration.phone_number,
                        'date_of_birth': registration.date_of_birth,
                    }
                )
                
                # Link the voter to registration
                registration.linked_voter = voter
                registration.save()
                
                # Clear session
                del request.session['pending_registration_id']
                
                logger.info(f"Auto-approved and created voter account for {registration.full_name} (ID: {registration.voter_id_epic})")
                
            return JsonResponse({
                'success': True,
                'message': 'Registration completed successfully! You can now login and vote.',
                'redirect_url': '/registration-success/'
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Verification failed. Please try again.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def registration_success(request):
    """Registration success page"""
    return render(request, 'voting/registration_success.html')
