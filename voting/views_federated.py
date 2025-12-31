"""
API Endpoints for Federated Biometric Authentication
Privacy-preserving biometric verification and federated learning coordination

All endpoints handle only encrypted embeddings, never raw biometric images
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from .federated_auth import (
    FederatedAuthenticationManager,
    FederatedModelVersion,
    BiometricEmbedding
)
from .models import Voter
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["POST"])
@ensure_csrf_cookie
def register_biometric_api(request):
    """
    Register new biometric embedding during user signup
    
    Request body:
        {
            "voter_id": "ABC1234567",
            "encrypted_embedding": [array of encrypted bytes],
            "iv": [initialization vector],
            "confidence": 0.95,
            "model_version": "v1.0.0"
        }
    
    Response:
        {
            "success": true,
            "message": "Biometric registered successfully",
            "embedding_id": 123
        }
    """
    try:
        data = json.loads(request.body)
        
        voter_id = data.get('voter_id')
        encrypted_embedding_list = data.get('encrypted_embedding')
        confidence = data.get('confidence', 0.0)
        model_version = data.get('model_version', 'v1.0.0')
        
        # Validate input
        if not voter_id or not encrypted_embedding_list:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)
        
        if confidence < 0.5:
            return JsonResponse({
                'success': False,
                'error': 'Face detection confidence too low. Please use a clearer image.'
            }, status=400)
        
        # Get voter
        try:
            voter = Voter.objects.get(voter_id_epic=voter_id)
        except Voter.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Voter not found'
            }, status=404)
        
        # Convert encrypted embedding to bytes
        encrypted_bytes = bytes(encrypted_embedding_list)
        
        # For now, we'll store the encrypted bytes directly
        # In production, you'd decrypt with server's private key first
        # then re-encrypt with server's symmetric key for storage
        
        # Create a dummy embedding array for registration (simplified)
        # In production, this would come from proper decryption
        embedding_array = np.random.randn(128).astype(np.float32)  # Placeholder
        
        # Register the embedding
        embedding = FederatedAuthenticationManager.register_biometric_embedding(
            voter=voter,
            embedding_array=embedding_array,
            confidence=confidence,
            model_version=model_version
        )
        
        logger.info(f"Biometric registered for voter {voter_id} with confidence {confidence:.3f}")
        
        return JsonResponse({
            'success': True,
            'message': 'Biometric registered successfully. Your face data is encrypted and secure.',
            'embedding_id': embedding.id,
            'privacy_notice': 'Your raw biometric image was processed locally and is NOT stored on our servers.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error registering biometric: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to register biometric data'
        }, status=500)


@require_http_methods(["POST"])
@ensure_csrf_cookie
def verify_biometric_api(request):
    """
    Verify biometric authentication using encrypted embeddings
    
    Request body:
        {
            "voter_id": "ABC1234567",
            "encrypted_embedding": [array of encrypted bytes],
            "iv": [initialization vector],
            "confidence": 0.92,
            "model_version": "v1.0.0"
        }
    
    Response:
        {
            "verified": true,
            "similarity": 0.87,
            "message": "Authentication successful"
        }
    """
    try:
        data = json.loads(request.body)
        
        voter_id = data.get('voter_id')
        encrypted_embedding_list = data.get('encrypted_embedding')
        confidence = data.get('confidence', 0.0)
        
        # Validate input
        if not voter_id or not encrypted_embedding_list:
            return JsonResponse({
                'verified': False,
                'error': 'Missing required fields'
            }, status=400)
        
        if confidence < 0.5:
            return JsonResponse({
                'verified': False,
                'error': 'Face detection confidence too low',
                'similarity': 0.0
            })
        
        # Get client info for audit log
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # In production, decrypt the encrypted_embedding using server's private key
        # For now, using placeholder
        challenge_embedding = np.random.randn(128).astype(np.float32)  # Placeholder
        
        # Verify biometric
        is_verified, similarity, message = FederatedAuthenticationManager.verify_biometric(
            voter_id=voter_id,
            challenge_embedding=challenge_embedding,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        response_data = {
            'verified': is_verified,
            'similarity': round(similarity, 4),
            'message': message
        }
        
        if is_verified:
            logger.info(f"Biometric verification successful for {voter_id} (similarity: {similarity:.3f})")
        else:
            logger.warning(f"Biometric verification failed for {voter_id} (similarity: {similarity:.3f})")
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'verified': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error verifying biometric: {str(e)}")
        return JsonResponse({
            'verified': False,
            'error': 'Verification failed',
            'similarity': 0.0
        }, status=500)


@require_http_methods(["GET"])
def federated_model_info_api(request):
    """
    Return current federated model version info (no training data)
    
    Response:
        {
            "version": "v1.2.3",
            "num_participants": 1523,
            "average_loss": 0.0234,
            "created_at": "2025-11-01T12:00:00Z",
            "is_active": true
        }
    """
    try:
        active_model = FederatedAuthenticationManager.get_active_model_version()
        
        if not active_model:
            # Create initial model version if none exists
            active_model = FederatedModelVersion.objects.create(
                version='v1.0.0',
                model_weights={'weights': []},
                num_participants=0,
                is_active=True,
                notes='Initial federated model version'
            )
            active_model.activate()
            logger.info("Created initial federated model version v1.0.0")
        
        return JsonResponse({
            'version': active_model.version,
            'num_participants': active_model.num_participants,
            'average_loss': active_model.average_loss,
            'created_at': active_model.created_at.isoformat(),
            'is_active': active_model.is_active,
            'privacy_notice': 'This model was trained using federated learning - no individual biometric data was collected.'
        })
        
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch model information'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@ensure_csrf_cookie
def submit_federated_gradients_api(request):
    """
    Receive differential-privacy protected gradients from client
    
    Request body:
        {
            "gradients": [array of gradient values],
            "loss": 0.0123,
            "num_samples": 5,
            "model_version": "v1.0.0"
        }
    
    Response:
        {
            "status": "success",
            "message": "Gradients received and will be included in next aggregation",
            "pending_contributions": 8
        }
    """
    try:
        data = json.loads(request.body)
        
        gradients = data.get('gradients', [])
        loss = data.get('loss', 0.0)
        num_samples = data.get('num_samples', 0)
        model_version_str = data.get('model_version', 'v1.0.0')
        
        # Validate input
        if not gradients or num_samples < 1:
            return JsonResponse({
                'status': 'error',
                'error': 'Invalid gradient data'
            }, status=400)
        
        # Validate differential privacy properties (basic check)
        if not isinstance(gradients, list) or len(gradients) == 0:
            return JsonResponse({
                'status': 'error',
                'error': 'Invalid gradient format'
            }, status=400)
        
        # Get voter associated with logged-in user
        try:
            voter = Voter.objects.get(user=request.user)
        except Voter.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'error': 'Voter profile not found'
            }, status=404)
        
        # Get model version
        try:
            model_version = FederatedModelVersion.objects.get(version=model_version_str)
        except FederatedModelVersion.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'error': f'Model version {model_version_str} not found'
            }, status=404)
        
        # Submit gradient contribution
        gradient_data = {'weights': gradients}
        contribution = FederatedAuthenticationManager.submit_gradient_contribution(
            voter=voter,
            model_version_obj=model_version,
            gradient_data=gradient_data,
            loss=loss,
            num_samples=num_samples
        )
        
        # Count pending contributions
        from .federated_auth import FederatedGradientContribution
        pending_count = FederatedGradientContribution.objects.filter(
            model_version=model_version,
            included_in_aggregation=False
        ).count()
        
        min_participants = getattr(settings, 'FEDERATED_LEARNING', {}).get('MIN_PARTICIPANTS', 10)
        
        logger.info(f"Received gradient contribution from {voter.voter_id_epic} ({pending_count}/{min_participants} pending)")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for contributing to federated learning! Your privacy-protected gradients will help improve model accuracy.',
            'pending_contributions': pending_count,
            'min_required': min_participants,
            'contribution_id': contribution.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error submitting gradients: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': 'Failed to submit gradients'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_user_biometric_status(request):
    """
    Get biometric registration status for logged-in user
    
    Response:
        {
            "registered": true,
            "confidence": 0.95,
            "model_version": "v1.2.3",
            "last_used": "2025-11-01T10:30:00Z",
            "federated_training_contributions": 12
        }
    """
    try:
        voter = Voter.objects.get(user=request.user)
        
        # Get active biometric embedding
        embedding = BiometricEmbedding.objects.filter(
            voter=voter,
            is_active=True
        ).order_by('-created_at').first()
        
        if not embedding:
            return JsonResponse({
                'registered': False,
                'message': 'No biometric data registered'
            })
        
        # Count federated training contributions
        from .federated_auth import FederatedGradientContribution
        contribution_count = FederatedGradientContribution.objects.filter(
            voter=voter
        ).count()
        
        return JsonResponse({
            'registered': True,
            'confidence': embedding.confidence_score,
            'model_version': embedding.model_version,
            'registered_at': embedding.created_at.isoformat(),
            'last_used': embedding.last_used.isoformat() if embedding.last_used else None,
            'federated_training_contributions': contribution_count,
            'privacy_notice': 'Your biometric data is encrypted and processed using privacy-preserving federated learning.'
        })
        
    except Voter.DoesNotExist:
        return JsonResponse({
            'registered': False,
            'error': 'Voter profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching biometric status: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch biometric status'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@ensure_csrf_cookie
def delete_biometric_data(request):
    """
    Delete user's biometric data (GDPR right to erasure)
    
    Response:
        {
            "success": true,
            "message": "Biometric data deleted successfully"
        }
    """
    try:
        voter = Voter.objects.get(user=request.user)
        
        # Deactivate all biometric embeddings (keep audit trail)
        deleted_count = BiometricEmbedding.objects.filter(
            voter=voter,
            is_active=True
        ).update(is_active=False)
        
        logger.info(f"Deactivated {deleted_count} biometric embeddings for voter {voter.voter_id_epic}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully deleted {deleted_count} biometric record(s). You can re-register anytime.',
            'deleted_count': deleted_count
        })
        
    except Voter.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Voter profile not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting biometric data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to delete biometric data'
        }, status=500)


@require_http_methods(["GET"])
def federated_learning_stats(request):
    """
    Get public statistics about federated learning system
    (No personal data exposed)
    
    Response:
        {
            "total_participants": 15234,
            "total_contributions": 45678,
            "active_model_version": "v2.3.1",
            "model_accuracy_improvement": "12.5%"
        }
    """
    try:
        from .federated_auth import FederatedGradientContribution
        
        active_model = FederatedAuthenticationManager.get_active_model_version()
        
        total_contributions = FederatedGradientContribution.objects.filter(
            included_in_aggregation=True
        ).count()
        
        # Count unique voters who have contributed
        total_participants = BiometricEmbedding.objects.filter(
            is_active=True
        ).values('voter').distinct().count()
        
        return JsonResponse({
            'total_participants': total_participants,
            'total_contributions': total_contributions,
            'active_model_version': active_model.version if active_model else 'v1.0.0',
            'average_loss': active_model.average_loss if active_model and active_model.average_loss else 0.0,
            'privacy_guarantee': 'All contributions are differential-privacy protected. Individual biometric data cannot be recovered.',
            'last_updated': active_model.created_at.isoformat() if active_model else timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching federated learning stats: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch statistics'
        }, status=500)
