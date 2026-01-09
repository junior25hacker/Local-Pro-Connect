from __future__ import annotations

from .models import ProviderProfile, UserProfile


def user_flags(request):
    """Template context flags + related profile objects.

    Keeps navigation and avatar rendering safe (no RelatedObjectDoesNotExist errors in templates).
    """
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {"is_provider": False, "provider_profile": None, "user_profile": None}

    provider_profile = ProviderProfile.objects.filter(user=user).first()
    user_profile = UserProfile.objects.filter(user=user).first()

    return {
        "is_provider": provider_profile is not None,
        "provider_profile": provider_profile,
        "user_profile": user_profile,
    }
