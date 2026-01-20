"""
Professional Filtering Utilities
Provides optimized filtering, sorting, and pagination for professionals.
"""

from django.db.models import Q, F
from decimal import Decimal
from .models import ProviderProfile


class ProfessionalFilter:
    """
    Handles complex filtering of professionals with support for:
    - Service type
    - Location (city, state, region)
    - Rating
    - Experience
    - Price range
    - Verification status
    
    Uses Django ORM optimizations (select_related, prefetch_related)
    """
    
    # Price range mappings
    PRICE_RANGES = {
        'budget': (0, 50),           # Under $50
        'moderate': (50, 150),       # $50-$150
        'premium': (150, 300),       # $150-$300
        'luxury': (300, 9999),       # $300+
    }
    
    # Cameroon regions/states
    REGIONS = [
        'adamawa',
        'centre',
        'east',
        'far_north',
        'littoral',
        'north',
        'northwest',
        'south',
        'southwest',
        'west',
    ]
    
    def __init__(self):
        """Initialize the filter with base queryset"""
        self.queryset = ProviderProfile.objects.filter(
            user__is_active=True
        ).select_related('user').defer('service_description')
        self.filters = {}
    
    def apply_service_filter(self, service_type):
        """
        Filter by service type.
        
        Args:
            service_type (str): Service type to filter by ('all' means no filter)
            
        Returns:
            self (for chaining)
        """
        if service_type and service_type != 'all':
            valid_services = [choice[0] for choice in ProviderProfile.SERVICE_CHOICES]
            if service_type in valid_services:
                self.queryset = self.queryset.filter(service_type=service_type)
                self.filters['service_type'] = service_type
        return self
    
    def apply_location_filter(self, location=None, city=None, state=None, region=None):
        """
        Filter by location (city, state, or region).
        
        Args:
            location (str): General location search (searches city, state, address)
            city (str): Specific city filter
            state (str): Specific state filter
            region (str): Region/state filter (case-insensitive)
            
        Returns:
            tuple: (self, region_message) where region_message indicates if no results
        """
        region_message = None
        original_count = self.queryset.count()
        
        # Apply specific filters
        if city:
            self.queryset = self.queryset.filter(city__iexact=city)
            self.filters['city'] = city
        
        if state:
            self.queryset = self.queryset.filter(state__iexact=state)
            self.filters['state'] = state
        
        # Apply region filter (matches state field)
        if region:
            region_lower = region.lower().strip()
            region_professionals = self.queryset.filter(state__iexact=region_lower)
            
            if region_professionals.count() == 0 and original_count > 0:
                # No professionals found in this region
                region_message = f"No professionals found in {region.title()}. Showing professionals from other regions."
                self.filters['region_not_found'] = region_lower
            else:
                self.queryset = region_professionals
                self.filters['region'] = region_lower
        
        # Apply general location search
        if location:
            self.queryset = self.queryset.filter(
                Q(city__icontains=location) |
                Q(state__icontains=location) |
                Q(business_address__icontains=location) |
                Q(company_name__icontains=location)
            )
            self.filters['location'] = location
        
        return self, region_message
    
    def apply_rating_filter(self, min_rating):
        """
        Filter by minimum rating.
        
        Args:
            min_rating (float or str): Minimum rating (e.g., 3.5, 4.0, 4.5)
            
        Returns:
            self (for chaining)
        """
        if min_rating:
            try:
                min_rating_float = float(min_rating)
                # Validate rating is between 0 and 5
                if 0 <= min_rating_float <= 5:
                    self.queryset = self.queryset.filter(rating__gte=min_rating_float)
                    self.filters['min_rating'] = min_rating_float
            except (ValueError, TypeError):
                pass  # Ignore invalid values
        return self
    
    def apply_experience_filter(self, min_experience):
        """
        Filter by minimum years of experience.
        
        Args:
            min_experience (int or str): Minimum years of experience
            
        Returns:
            self (for chaining)
        """
        if min_experience:
            try:
                min_exp_int = int(min_experience)
                if min_exp_int >= 0:
                    self.queryset = self.queryset.filter(years_experience__gte=min_exp_int)
                    self.filters['min_experience'] = min_exp_int
            except (ValueError, TypeError):
                pass  # Ignore invalid values
        return self
    
    def apply_price_filter(self, price_range=None, min_price=None, max_price=None):
        """
        Filter by price range.
        
        Args:
            price_range (str): Preset range ('budget', 'moderate', 'premium', 'luxury')
            min_price (float or str): Minimum price (overrides preset)
            max_price (float or str): Maximum price (overrides preset)
            
        Returns:
            self (for chaining)
        """
        min_p = None
        max_p = None
        
        # Use preset if provided and no explicit min/max
        if price_range and price_range in self.PRICE_RANGES:
            min_p, max_p = self.PRICE_RANGES[price_range]
            self.filters['price_range'] = price_range
        
        # Override with explicit min/max if provided
        if min_price:
            try:
                min_p = float(min_price)
            except (ValueError, TypeError):
                pass
        
        if max_price:
            try:
                max_p = float(max_price)
            except (ValueError, TypeError):
                pass
        
        # Apply filter if we have valid bounds
        if min_p is not None:
            self.queryset = self.queryset.filter(min_price__gte=min_p)
            self.filters['min_price'] = min_p
        
        if max_p is not None:
            self.queryset = self.queryset.filter(min_price__lte=max_p)
            self.filters['max_price'] = max_p
        
        return self
    
    def apply_verified_filter(self, verified_only=False):
        """
        Filter to show only verified professionals.
        
        Args:
            verified_only (bool): If True, filter to verified only
            
        Returns:
            self (for chaining)
        """
        if verified_only:
            self.queryset = self.queryset.filter(is_verified=True)
            self.filters['verified_only'] = True
        return self
    
    def apply_review_count_filter(self, min_reviews=None):
        """
        Filter by minimum number of reviews.
        
        Args:
            min_reviews (int or str): Minimum number of reviews
            
        Returns:
            self (for chaining)
        """
        if min_reviews:
            try:
                min_reviews_int = int(min_reviews)
                if min_reviews_int >= 0:
                    self.queryset = self.queryset.filter(total_reviews__gte=min_reviews_int)
                    self.filters['min_reviews'] = min_reviews_int
            except (ValueError, TypeError):
                pass
        return self
    
    def sort_by(self, sort_field='rating'):
        """
        Sort professionals by field.
        
        Args:
            sort_field (str): Field to sort by
                - 'rating': Highest rating first (default)
                - 'reviews': Most reviews first
                - 'price': Lowest price first
                - 'experience': Most experience first
                - 'newest': Newly added first
                - 'name': Alphabetical by company name
            
        Returns:
            self (for chaining)
        """
        sort_mapping = {
            'rating': ['-rating', '-created_at'],
            'reviews': ['-total_reviews', '-rating'],
            'price': ['min_price', '-rating'],
            'experience': ['-years_experience', '-rating'],
            'newest': ['-created_at'],
            'name': ['company_name'],
        }
        
        sort_fields = sort_mapping.get(sort_field, ['-rating', '-created_at'])
        self.queryset = self.queryset.order_by(*sort_fields)
        self.filters['sort'] = sort_field
        
        return self
    
    def paginate(self, page=1, limit=20):
        """
        Apply pagination to queryset.
        
        Args:
            page (int): Page number (1-indexed)
            limit (int): Items per page (1-100)
            
        Returns:
            dict: {
                'items': paginated_queryset,
                'page': current_page,
                'limit': items_per_page,
                'total': total_count,
                'pages': total_pages,
                'has_next': bool,
                'has_prev': bool,
            }
        """
        # Validate inputs
        try:
            page = max(1, int(page))
            limit = max(1, min(100, int(limit)))  # Cap at 100
        except (ValueError, TypeError):
            page = 1
            limit = 20
        
        total_count = self.queryset.count()
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        offset = (page - 1) * limit
        items = self.queryset[offset:offset + limit]
        
        return {
            'items': items,
            'page': page,
            'limit': limit,
            'total': total_count,
            'pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'offset': offset,
        }
    
    def get_queryset(self):
        """Get the current queryset"""
        return self.queryset
    
    def get_filters_applied(self):
        """Get dictionary of filters that were applied"""
        return self.filters.copy()
    
    def count(self):
        """Get count of results"""
        return self.queryset.count()


def serialize_professional(professional):
    """
    Convert a ProviderProfile instance to a JSON-serializable dictionary.
    
    Args:
        professional (ProviderProfile): The provider to serialize
        
    Returns:
        dict: Serialized professional data
    """
    return {
        'id': professional.id,
        'name': professional.company_name or professional.user.get_full_name() or professional.user.username,
        'company': professional.company_name,
        'avatar': professional.profile_picture.url if professional.profile_picture else None,
        'service': professional.get_service_type_display(),
        'serviceType': professional.service_type,
        'rating': float(professional.rating) if professional.rating else 0.0,
        'reviews': professional.total_reviews if professional.total_reviews else 0,
        'verified': professional.is_verified,
        'experience': professional.years_experience if professional.years_experience else 0,
        'price_range': determine_price_range(professional.min_price),
        'min_price': float(professional.min_price) if professional.min_price else 50.0,
        'location': f"{professional.city}, {professional.state}" if professional.city and professional.state else 'Location not available',
        'city': professional.city,
        'state': professional.state,
        'region': professional.state,
        'bio': professional.bio or '',
        'phone': professional.phone or '',
        'verified_badge': professional.is_verified,
    }


def determine_price_range(min_price):
    """
    Determine price range symbol based on minimum price.
    
    Args:
        min_price (Decimal or float): Minimum price
        
    Returns:
        str: Price range symbol with CFA indicator
    """
    try:
        price = float(min_price) if min_price else 0
        if price < 50:
            return 'CFA'
        elif price < 150:
            return 'CFA'
        elif price < 300:
            return 'CFA'
        else:
            return 'CFA'
    except (ValueError, TypeError):
        return 'CFA'


def get_region_alternatives(queryset):
    """
    Get list of alternative regions with professionals.
    
    Args:
        queryset: ProviderProfile queryset
        
    Returns:
        list: Sorted list of regions with professionals
    """
    regions = set()
    for professional in queryset:
        if professional.state:
            regions.add(professional.state)
    return sorted(list(regions))
