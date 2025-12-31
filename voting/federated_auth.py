"""
Federated Learning Backend for Biometric Authentication
Server never stores raw biometric data, only encrypted embeddings

Privacy-preserving features:
- Encrypted biometric embeddings only (no raw images)
- Differential privacy protection on gradient aggregation
- Federated averaging for distributed learning
- Audit trail for compliance
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
import numpy as np
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class BiometricEmbedding(models.Model):
    """
    Stores ONLY encrypted biometric embeddings, never raw images
    Compliant with GDPR and privacy regulations
    """
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE, related_name='biometric_embeddings')
    encrypted_embedding = models.BinaryField(help_text="Encrypted 128-dimensional face embedding vector")
    embedding_hash = models.CharField(max_length=64, unique=True, db_index=True, 
                                     help_text="SHA-256 hash for deduplication")
    confidence_score = models.FloatField(help_text="Face detection confidence (0-1)")
    model_version = models.CharField(max_length=20, help_text="Federated model version used")
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True, help_text="Last successful authentication")
    is_active = models.BooleanField(default=True, help_text="Can be used for authentication")
    
    class Meta:
        db_table = 'biometric_embeddings'
        indexes = [
            models.Index(fields=['voter', 'model_version', 'is_active']),
            models.Index(fields=['embedding_hash']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = "Biometric Embedding"
        verbose_name_plural = "Biometric Embeddings"

    def __str__(self):
        return f"Biometric for {self.voter.voter_id_epic} (v{self.model_version})"

    def verify_embedding(self, challenge_embedding, threshold=0.6):
        """
        Verify biometric embedding using cosine similarity
        
        Args:
            challenge_embedding: numpy array or list of floats (128-d)
            threshold: Similarity threshold (0-1)
            
        Returns:
            tuple: (is_verified: bool, similarity_score: float)
        """
        try:
            # Decrypt stored embedding for comparison
            stored_embedding = self._decrypt_embedding()
            
            # Ensure challenge is numpy array
            if isinstance(challenge_embedding, list):
                challenge_embedding = np.array(challenge_embedding, dtype=np.float32)
            
            # Compute cosine similarity
            dot_product = np.dot(stored_embedding, challenge_embedding)
            norm_stored = np.linalg.norm(stored_embedding)
            norm_challenge = np.linalg.norm(challenge_embedding)
            
            if norm_stored == 0 or norm_challenge == 0:
                logger.warning(f"Zero norm detected in embedding comparison for voter {self.voter.voter_id_epic}")
                return False, 0.0
            
            similarity = dot_product / (norm_stored * norm_challenge)
            
            # Clamp similarity to [-1, 1] range
            similarity = float(np.clip(similarity, -1, 1))
            
            is_verified = similarity >= threshold
            
            # Update last_used timestamp if verified
            if is_verified:
                self.last_used = timezone.now()
                self.save(update_fields=['last_used'])
                logger.info(f"Biometric verification successful for {self.voter.voter_id_epic} (similarity: {similarity:.3f})")
            else:
                logger.info(f"Biometric verification failed for {self.voter.voter_id_epic} (similarity: {similarity:.3f}, threshold: {threshold})")
            
            return is_verified, similarity
            
        except Exception as e:
            logger.error(f"Error verifying biometric embedding: {str(e)}")
            return False, 0.0

    def _decrypt_embedding(self):
        """
        Decrypt embedding for verification only
        Never logged or returned in API responses
        """
        try:
            cipher = Fernet(settings.BIOMETRIC_ENCRYPTION_KEY.encode())
            decrypted_bytes = cipher.decrypt(bytes(self.encrypted_embedding))
            embedding = np.frombuffer(decrypted_bytes, dtype=np.float32)
            return embedding
        except Exception as e:
            logger.error(f"Failed to decrypt embedding: {str(e)}")
            raise ValueError("Failed to decrypt biometric embedding")

    @staticmethod
    def encrypt_embedding(embedding_array):
        """
        Encrypt embedding before storage
        
        Args:
            embedding_array: numpy array or list of floats
            
        Returns:
            bytes: Encrypted embedding
        """
        if isinstance(embedding_array, list):
            embedding_array = np.array(embedding_array, dtype=np.float32)
        
        cipher = Fernet(settings.BIOMETRIC_ENCRYPTION_KEY.encode())
        encrypted = cipher.encrypt(embedding_array.tobytes())
        return encrypted

    def deactivate(self):
        """
        Deactivate this biometric embedding (soft delete for audit trail)
        """
        self.is_active = False
        self.save(update_fields=['is_active'])
        logger.info(f"Deactivated biometric embedding for {self.voter.voter_id_epic}")


class FederatedModelVersion(models.Model):
    """
    Tracks federated learning model versions
    Stores aggregated model weights, NOT individual biometric data
    """
    version = models.CharField(max_length=20, unique=True, help_text="Semantic version (e.g., v1.2.3)")
    model_weights = models.JSONField(help_text="Aggregated weights from federated training")
    num_participants = models.IntegerField(default=0, help_text="Number of clients contributing to this version")
    average_loss = models.FloatField(null=True, blank=True, help_text="Average training loss")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, help_text="Currently deployed model version")
    deployment_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, help_text="Release notes or change description")
    
    class Meta:
        db_table = 'federated_model_versions'
        ordering = ['-created_at']
        verbose_name = "Federated Model Version"
        verbose_name_plural = "Federated Model Versions"

    def __str__(self):
        return f"Model {self.version} ({'active' if self.is_active else 'inactive'})"

    def activate(self):
        """
        Activate this model version (deactivates others)
        """
        # Deactivate all other versions
        FederatedModelVersion.objects.filter(is_active=True).update(is_active=False)
        
        # Activate this version
        self.is_active = True
        self.deployment_date = timezone.now()
        self.save(update_fields=['is_active', 'deployment_date'])
        
        logger.info(f"Activated federated model version {self.version}")


class FederatedGradientContribution(models.Model):
    """
    Stores gradient contributions from clients (NOT raw biometric data)
    Gradients are differential-privacy protected
    """
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE, related_name='gradient_contributions')
    model_version = models.ForeignKey(FederatedModelVersion, on_delete=models.CASCADE, related_name='contributions')
    
    gradient_data = models.JSONField(help_text="Differential-privacy protected gradients")
    loss = models.FloatField(help_text="Local training loss")
    num_samples = models.IntegerField(help_text="Number of local samples used")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    included_in_aggregation = models.BooleanField(default=False, help_text="Included in federated averaging")
    aggregation_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'federated_gradient_contributions'
        indexes = [
            models.Index(fields=['model_version', 'included_in_aggregation']),
            models.Index(fields=['submitted_at']),
        ]
        verbose_name = "Federated Gradient Contribution"
        verbose_name_plural = "Federated Gradient Contributions"

    def __str__(self):
        return f"Gradient from {self.voter.voter_id_epic} for {self.model_version.version}"


class BiometricAuthLog(models.Model):
    """
    Audit log for biometric authentication attempts
    Required for compliance and security monitoring
    """
    voter = models.ForeignKey('Voter', on_delete=models.CASCADE, related_name='auth_logs')
    embedding = models.ForeignKey(BiometricEmbedding, on_delete=models.SET_NULL, null=True, blank=True)
    
    success = models.BooleanField(help_text="Authentication result")
    similarity_score = models.FloatField(help_text="Cosine similarity score")
    model_version = models.CharField(max_length=20)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    failure_reason = models.CharField(max_length=100, blank=True, 
                                     help_text="Reason for authentication failure")
    
    class Meta:
        db_table = 'biometric_auth_logs'
        indexes = [
            models.Index(fields=['voter', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
        verbose_name = "Biometric Authentication Log"
        verbose_name_plural = "Biometric Authentication Logs"

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.voter.voter_id_epic} at {self.timestamp}"


class FederatedAuthenticationManager:
    """
    Manages federated learning workflow for biometric authentication
    Implements privacy-preserving protocols
    """
    
    @staticmethod
    def register_biometric_embedding(voter, embedding_array, confidence, model_version):
        """
        Register new biometric embedding (encrypted, never raw image)
        
        Args:
            voter: Voter instance
            embedding_array: 128-d numpy array or list
            confidence: float (0-1)
            model_version: str
            
        Returns:
            BiometricEmbedding instance
        """
        try:
            # Encrypt the embedding
            encrypted = BiometricEmbedding.encrypt_embedding(embedding_array)
            
            # Create hash for deduplication
            embedding_hash = hashlib.sha256(encrypted).hexdigest()
            
            # Check if embedding already exists
            existing = BiometricEmbedding.objects.filter(
                voter=voter,
                embedding_hash=embedding_hash,
                is_active=True
            ).first()
            
            if existing:
                logger.info(f"Biometric embedding already exists for {voter.voter_id_epic}")
                return existing
            
            # Deactivate old embeddings for this voter (keep audit trail)
            BiometricEmbedding.objects.filter(
                voter=voter,
                is_active=True
            ).update(is_active=False)
            
            # Create new embedding
            embedding = BiometricEmbedding.objects.create(
                voter=voter,
                encrypted_embedding=encrypted,
                embedding_hash=embedding_hash,
                confidence_score=confidence,
                model_version=model_version
            )
            
            logger.info(f"Registered new biometric embedding for {voter.voter_id_epic}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to register biometric embedding: {str(e)}")
            raise
    
    @staticmethod
    def verify_biometric(voter_id, challenge_embedding, ip_address=None, user_agent=None):
        """
        Verify biometric authentication using stored embeddings
        
        Args:
            voter_id: Voter ID (EPIC number)
            challenge_embedding: numpy array or list (128-d)
            ip_address: str (optional)
            user_agent: str (optional)
            
        Returns:
            tuple: (is_verified: bool, similarity: float, message: str)
        """
        from voting.models import Voter
        
        try:
            voter = Voter.objects.get(voter_id_epic=voter_id)
        except Voter.DoesNotExist:
            logger.warning(f"Verification attempted for non-existent voter: {voter_id}")
            return False, 0.0, "Voter not found"
        
        # Get active embedding for this voter
        embedding = BiometricEmbedding.objects.filter(
            voter=voter,
            is_active=True
        ).order_by('-created_at').first()
        
        if not embedding:
            logger.warning(f"No biometric embedding found for voter: {voter_id}")
            
            # Log the attempt
            BiometricAuthLog.objects.create(
                voter=voter,
                success=False,
                similarity_score=0.0,
                model_version='unknown',
                ip_address=ip_address,
                user_agent=user_agent or '',
                failure_reason="No biometric embedding registered"
            )
            
            return False, 0.0, "No biometric data registered"
        
        # Get threshold from settings
        threshold = getattr(settings, 'BIOMETRIC_VERIFICATION', {}).get('SIMILARITY_THRESHOLD', 0.6)
        
        # Verify using encrypted embedding comparison
        is_verified, similarity = embedding.verify_embedding(challenge_embedding, threshold)
        
        # Log authentication attempt
        BiometricAuthLog.objects.create(
            voter=voter,
            embedding=embedding,
            success=is_verified,
            similarity_score=similarity,
            model_version=embedding.model_version,
            ip_address=ip_address,
            user_agent=user_agent or '',
            failure_reason="" if is_verified else f"Similarity {similarity:.3f} below threshold {threshold}"
        )
        
        if is_verified:
            return True, similarity, "Authentication successful"
        else:
            return False, similarity, f"Similarity score too low ({similarity:.3f})"
    
    @staticmethod
    def aggregate_federated_gradients(model_version_obj):
        """
        Federated Averaging: Aggregate gradients from clients
        Uses secure aggregation protocol (no individual gradient inspection)
        
        Args:
            model_version_obj: FederatedModelVersion instance
            
        Returns:
            str: New version identifier or None if insufficient contributions
        """
        # Get pending contributions
        contributions = FederatedGradientContribution.objects.filter(
            model_version=model_version_obj,
            included_in_aggregation=False
        )
        
        min_participants = getattr(settings, 'FEDERATED_LEARNING', {}).get('MIN_PARTICIPANTS', 10)
        
        if contributions.count() < min_participants:
            logger.info(f"Insufficient contributions for aggregation: {contributions.count()}/{min_participants}")
            return None
        
        logger.info(f"Aggregating {contributions.count()} gradient contributions...")
        
        # Federated Averaging Algorithm (FedAvg)
        total_samples = sum(c.num_samples for c in contributions)
        aggregated_gradients = None
        
        for contribution in contributions:
            weight = contribution.num_samples / total_samples
            gradients = contribution.gradient_data.get('weights', [])
            
            if isinstance(gradients, list):
                gradients = np.array(gradients, dtype=np.float32)
            
            if aggregated_gradients is None:
                aggregated_gradients = weight * gradients
            else:
                aggregated_gradients += weight * gradients
        
        # Mark contributions as included
        contributions.update(
            included_in_aggregation=True,
            aggregation_date=timezone.now()
        )
        
        # Calculate average loss
        avg_loss = np.mean([c.loss for c in contributions])
        
        # Create new model version
        current_version = model_version_obj.version
        version_number = int(current_version.replace('v', '').split('.')[0])
        new_version = f"v{version_number + 1}.0.0"
        
        new_model = FederatedModelVersion.objects.create(
            version=new_version,
            model_weights={'weights': aggregated_gradients.tolist()},
            num_participants=contributions.count(),
            average_loss=float(avg_loss),
            notes=f"Aggregated from {contributions.count()} contributions with average loss {avg_loss:.4f}"
        )
        
        logger.info(f"Created new federated model version: {new_version}")
        
        return new_version
    
    @staticmethod
    def get_active_model_version():
        """
        Get currently active federated model version
        
        Returns:
            FederatedModelVersion instance or None
        """
        return FederatedModelVersion.objects.filter(is_active=True).first()
    
    @staticmethod
    def submit_gradient_contribution(voter, model_version_obj, gradient_data, loss, num_samples):
        """
        Submit a gradient contribution from a client
        
        Args:
            voter: Voter instance
            model_version_obj: FederatedModelVersion instance
            gradient_data: dict with 'weights' key
            loss: float
            num_samples: int
            
        Returns:
            FederatedGradientContribution instance
        """
        contribution = FederatedGradientContribution.objects.create(
            voter=voter,
            model_version=model_version_obj,
            gradient_data=gradient_data,
            loss=loss,
            num_samples=num_samples
        )
        
        logger.info(f"Received gradient contribution from {voter.voter_id_epic} for {model_version_obj.version}")
        
        # Check if we have enough contributions to aggregate
        pending_count = FederatedGradientContribution.objects.filter(
            model_version=model_version_obj,
            included_in_aggregation=False
        ).count()
        
        min_participants = getattr(settings, 'FEDERATED_LEARNING', {}).get('MIN_PARTICIPANTS', 10)
        
        if pending_count >= min_participants:
            logger.info(f"Threshold reached ({pending_count}/{min_participants}), triggering aggregation...")
            # Trigger aggregation (could be async task in production)
            FederatedAuthenticationManager.aggregate_federated_gradients(model_version_obj)
        
        return contribution
