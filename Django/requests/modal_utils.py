"""
Modal utility functions for managing interactive modal interactions.

This module provides helper functions for:
- Modal state validation
- Request status transitions
- Modal response formatting
- Error message standardization
"""

import logging

logger = logging.getLogger(__name__)


class ModalStateValidator:
    """Validates request state transitions for modal operations."""
    
    VALID_STATE_TRANSITIONS = {
        'pending': ['accepted', 'declined'],
        'accepted': [],  # Terminal state
        'declined': [],  # Terminal state
    }
    
    @classmethod
    def can_accept(cls, current_status):
        """Check if request can be accepted from current status."""
        return current_status in ['pending'] and 'accepted' in cls.VALID_STATE_TRANSITIONS.get(current_status, [])
    
    @classmethod
    def can_decline(cls, current_status):
        """Check if request can be declined from current status."""
        return current_status in ['pending'] and 'declined' in cls.VALID_STATE_TRANSITIONS.get(current_status, [])
    
    @classmethod
    def can_edit(cls, current_status):
        """Check if request can be edited from current status."""
        return current_status == 'pending'
    
    @classmethod
    def validate_transition(cls, from_status, to_status):
        """
        Validate that a state transition is allowed.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        valid_transitions = cls.VALID_STATE_TRANSITIONS.get(from_status, [])
        
        if to_status not in valid_transitions:
            return False, f"Cannot transition from '{from_status}' to '{to_status}'"
        
        return True, None


class ModalResponseBuilder:
    """Build standardized response objects for modal API endpoints."""
    
    @staticmethod
    def success(message, request_id=None, **kwargs):
        """Build a success response."""
        response = {
            'status': 'success',
            'message': message,
        }
        if request_id:
            response['request_id'] = request_id
        response.update(kwargs)
        return response
    
    @staticmethod
    def error(message, error_code='UNKNOWN_ERROR', status_code=400, **kwargs):
        """Build an error response."""
        response = {
            'status': 'error',
            'message': message,
            'error_code': error_code,
        }
        response.update(kwargs)
        return response, status_code
    
    @staticmethod
    def validation_error(errors, message='Validation failed.'):
        """Build a validation error response."""
        response = {
            'status': 'error',
            'message': message,
            'error_code': 'VALIDATION_ERROR',
            'errors': errors,
        }
        return response, 400
    
    @staticmethod
    def conflict(message, error_code='CONFLICT'):
        """Build a conflict response (409)."""
        response = {
            'status': 'error',
            'message': message,
            'error_code': error_code,
        }
        return response, 409
    
    @staticmethod
    def forbidden(message, error_code='FORBIDDEN'):
        """Build a forbidden response (403)."""
        response = {
            'status': 'error',
            'message': message,
            'error_code': error_code,
        }
        return response, 403
    
    @staticmethod
    def not_found(message, error_code='NOT_FOUND'):
        """Build a not found response (404)."""
        response = {
            'status': 'error',
            'message': message,
            'error_code': error_code,
        }
        return response, 404


class RequestPermissionValidator:
    """Validates user permissions for request operations."""
    
    @staticmethod
    def can_decline(service_request, user):
        """Check if user can decline the request."""
        if service_request.provider != user:
            return False, 'You do not have permission to decline this request.'
        
        if service_request.status == 'declined':
            return False, 'This request has already been declined.'
        
        if service_request.status == 'accepted':
            return False, 'Cannot decline an accepted request.'
        
        return True, None
    
    @staticmethod
    def can_accept(service_request, user):
        """Check if user can accept the request."""
        if service_request.provider != user:
            return False, 'You do not have permission to accept this request.'
        
        if service_request.status == 'accepted':
            return False, 'This request has already been accepted.'
        
        if service_request.status == 'declined':
            return False, 'Cannot accept a declined request.'
        
        return True, None
    
    @staticmethod
    def can_edit(service_request, user):
        """Check if user can edit the request."""
        if service_request.user != user:
            return False, 'You do not have permission to edit this request.'
        
        if service_request.status in ['accepted', 'declined']:
            return False, f'Cannot edit a {service_request.status} request.'
        
        return True, None


class ModalLogFormatter:
    """Format log messages for modal operations."""
    
    @staticmethod
    def log_decline(request_id, user, reason):
        """Format a decline log message."""
        return f"Request #{request_id} declined by provider {user.username} (reason: {reason})"
    
    @staticmethod
    def log_accept(request_id, user):
        """Format an accept log message."""
        return f"Request #{request_id} accepted by provider {user.username}"
    
    @staticmethod
    def log_edit(request_id, user, fields):
        """Format an edit log message."""
        fields_str = ', '.join(fields)
        return f"Request #{request_id} edited by user {user.username} (fields: {fields_str})"
    
    @staticmethod
    def log_unauthorized_attempt(request_id, user, action):
        """Format an unauthorized attempt log message."""
        return f"Unauthorized {action} attempt for request #{request_id} by user {user.username}"


def format_form_errors(form_errors):
    """
    Convert Django form errors to a simple dict format.
    
    Args:
        form_errors: Django form.errors object
    
    Returns:
        dict: Simple dictionary of field errors
    """
    errors = {}
    for field, messages in form_errors.items():
        if isinstance(messages, list):
            errors[field] = ' '.join(str(m) for m in messages)
        else:
            errors[field] = str(messages)
    return errors


def get_decline_reason_display(reason_code):
    """
    Get human-readable display text for decline reason.
    
    Args:
        reason_code: The decline reason code (e.g., 'price', 'distance', etc.)
    
    Returns:
        str: Human-readable reason text
    """
    REASON_DISPLAY = {
        'price': 'Price doesn\'t match my rate',
        'distance': 'Location is too far',
        'time': 'Schedule doesn\'t work',
        'other': 'Other reason',
    }
    return REASON_DISPLAY.get(reason_code, reason_code)
