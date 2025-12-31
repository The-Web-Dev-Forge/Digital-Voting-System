"""
Views for literacy assessment and ballot simplification
Handles user literacy profiling and adaptive ballot content generation
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .ballot_simplification import (
    BallotSimplificationEngine,
    UserLiteracyProfile,
    LiteracyLevel,
    BallotInteractionLog,
)
from .models import Voter, Candidate, Party
import json


def literacy_assessment_view(request):
    """
    Literacy level assessment page
    Can be accessed after login to set preferences
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.info(request, 'Please login first to customize your voting experience.')
        return redirect('login_page')
    
    # Try to get voter profile, but allow access even if it doesn't exist yet
    try:
        voter = Voter.objects.get(user=request.user)
        existing_profile = UserLiteracyProfile.objects.filter(voter=voter).first()
    except Voter.DoesNotExist:
        # User is logged in but doesn't have voter profile yet
        # Still show the form, but they can't save until they complete registration
        messages.warning(request, 'Please complete your voter registration first to save accessibility preferences.')
        existing_profile = None
        voter = None
    
    if request.method == 'POST':
        # Check if voter exists before saving
        if not voter:
            messages.error(request, 'Please complete voter registration first before saving preferences.')
            return redirect('user_register')
        
        # Process assessment responses
        responses = {
            'education_level': request.POST.get('education_level'),
            'reading_comfort': request.POST.get('reading_comfort'),
            'prefers_images': request.POST.get('prefers_images'),
            'needs_audio': request.POST.get('needs_audio'),
            'preferred_language': request.POST.get('preferred_language', 'en'),
            'font_size': request.POST.get('font_size', 'medium'),
        }
        
        # Assess literacy level
        literacy_level = BallotSimplificationEngine.assess_literacy_level(responses)
        
        # Create or update profile
        profile, created = UserLiteracyProfile.objects.update_or_create(
            voter=voter,
            defaults={
                'literacy_level': literacy_level,
                'preferred_language': responses['preferred_language'],
                'font_size_preference': responses['font_size'],
                'use_audio_assistance': responses['needs_audio'] == 'yes',
                'use_visual_aids': responses['prefers_images'] == 'yes',
                'cognitive_assistance_enabled': literacy_level in [
                    LiteracyLevel.BASIC,
                    LiteracyLevel.MINIMAL,
                    LiteracyLevel.VISUAL
                ],
            }
        )
        
        # Show success message
        if created:
            messages.success(request, '✓ Your accessibility settings have been saved successfully!')
        else:
            messages.success(request, '✓ Your accessibility settings have been updated!')
        
        # Redirect to voting page
        return redirect('vote')
    
    context = {
        'existing_profile': existing_profile,
        'languages': [
            ('en', 'English'),
            ('hi', 'हिंदी (Hindi)'),
            ('bn', 'বাংলা (Bengali)'),
            ('te', 'తెలుగు (Telugu)'),
            ('mr', 'मराठी (Marathi)'),
            ('ta', 'தமிழ் (Tamil)'),
        ],
    }
    
    return render(request, 'voting/literacy_assessment.html', context)


@login_required(login_url='login_page')
@require_http_methods(["GET"])
def get_simplified_ballot(request):
    """
    API endpoint to get simplified ballot content for all candidates
    
    Query params:
        - language: Language code (default: 'en')
    """
    try:
        voter = Voter.objects.get(user=request.user)
    except Voter.DoesNotExist:
        return JsonResponse({
            'error': 'Voter profile not found',
            'message': 'Please complete registration first',
            'redirect': '/register/'
        }, status=404)
    
    try:
        profile = UserLiteracyProfile.objects.get(voter=voter)
    except UserLiteracyProfile.DoesNotExist:
        return JsonResponse({
            'error': 'No accessibility profile found',
            'message': 'Please complete the accessibility assessment first',
            'redirect': '/accessibility-settings/'
        }, status=404)
    
    language = request.GET.get('language', profile.preferred_language)
    
    # Get all candidates for the voter's constituency
    candidates = Candidate.objects.filter(
        party__name__isnull=False  # Ensure party exists
    ).select_related('party')
    
    simplified_ballots = []
    
    for candidate in candidates:
        simplified = BallotSimplificationEngine.create_simplified_ballot(
            candidate=candidate,
            party=candidate.party,
            literacy_level=profile.literacy_level,
            language=language
        )
        
        # Get party symbol URL
        party_symbol_url = ''
        if candidate.party.symbol:
            party_symbol_url = request.build_absolute_uri(candidate.party.symbol.url)
        
        simplified_ballots.append({
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'party_name': candidate.party.name,
            'party_symbol': party_symbol_url,
            'simplified_content': simplified,
            'literacy_level': profile.literacy_level,
        })
    
    return JsonResponse({
        'ballots': simplified_ballots,
        'user_preferences': {
            'literacy_level': profile.get_literacy_level_display(),
            'language': language,
            'font_size': profile.font_size_preference,
            'audio_enabled': profile.use_audio_assistance,
            'visual_aids': profile.use_visual_aids,
            'cognitive_assistance': profile.cognitive_assistance_enabled,
        }
    })


@login_required(login_url='login_page')
@require_http_methods(["POST"])
def log_ballot_interaction(request):
    """
    Log user interaction with ballot content for adaptive learning
    """
    try:
        voter = Voter.objects.get(user=request.user)
        profile = UserLiteracyProfile.objects.get(voter=voter)
    except (Voter.DoesNotExist, UserLiteracyProfile.DoesNotExist):
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    candidate_id = data.get('candidate_id')
    interaction_type = data.get('interaction_type')
    time_spent = data.get('time_spent', 0)
    
    if not candidate_id or not interaction_type:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return JsonResponse({'error': 'Candidate not found'}, status=404)
    
    # Log interaction
    BallotInteractionLog.objects.create(
        voter=voter,
        candidate=candidate,
        interaction_type=interaction_type,
        time_spent=time_spent,
        literacy_level_at_time=profile.literacy_level,
    )
    
    # Update profile statistics
    help_requested = interaction_type in ['help', 'simplify', 'audio']
    profile.update_interaction_stats(
        reading_time=time_spent if interaction_type == 'view' else None,
        help_requested=help_requested
    )
    
    return JsonResponse({'status': 'success'})


@login_required(login_url='login_page')
@require_http_methods(["POST"])
def request_simplification(request):
    """
    Request real-time simplification of specific text
    Used when user clicks "Simplify" button on ballot
    """
    try:
        voter = Voter.objects.get(user=request.user)
        profile = UserLiteracyProfile.objects.get(voter=voter)
    except (Voter.DoesNotExist, UserLiteracyProfile.DoesNotExist):
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    text = data.get('text', '')
    
    if not text:
        return JsonResponse({'error': 'No text provided'}, status=400)
    
    # Simplify the text
    simplified = BallotSimplificationEngine.simplify_text(
        text=text,
        literacy_level=profile.literacy_level,
        language=profile.preferred_language
    )
    
    # Generate analogy if requested
    include_analogy = data.get('include_analogy', False)
    analogy = ''
    
    if include_analogy:
        # Try to detect policy concept
        for concept in BallotSimplificationEngine.POLICY_ANALOGIES.keys():
            if concept in text.lower():
                analogy = BallotSimplificationEngine.generate_analogy(
                    concept,
                    profile.literacy_level
                )
                break
    
    return JsonResponse({
        'simplified_text': simplified,
        'analogy': analogy,
        'literacy_level': profile.get_literacy_level_display(),
    })


@require_http_methods(["GET"])
def get_user_literacy_status(request):
    """
    Check if user has completed literacy assessment
    Used to redirect users to assessment page if needed
    No login required - returns status for any user
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'has_profile': False,
            'needs_assessment': True,
            'redirect_url': '/login/'
        })
    
    try:
        voter = Voter.objects.get(user=request.user)
        profile = UserLiteracyProfile.objects.filter(voter=voter).first()
        
        if profile:
            return JsonResponse({
                'has_profile': True,
                'literacy_level': profile.get_literacy_level_display(),
                'needs_assessment': False,
            })
        else:
            return JsonResponse({
                'has_profile': False,
                'needs_assessment': True,
                'redirect_url': '/accessibility-settings/'
            })
    except Voter.DoesNotExist:
        return JsonResponse({'error': 'Voter not found'}, status=404)
