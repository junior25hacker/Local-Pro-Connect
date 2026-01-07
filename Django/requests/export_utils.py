"""
Utility functions for exporting service request data to various formats.
"""
import csv
import io
from datetime import datetime
from decimal import Decimal

from django.db.models import Q, Count
from django.utils import timezone

from .models import ServiceRequest


def get_filtered_requests(user, filters=None, is_provider=False):
    """
    Get filtered service requests based on provided filters and user type.
    
    Args:
        user: The requesting user
        filters: Dictionary of filter parameters
        is_provider: Boolean indicating if user is a provider
    
    Returns:
        QuerySet of filtered ServiceRequest objects
    """
    # Start with base queryset
    if is_provider:
        queryset = ServiceRequest.objects.filter(
            provider=user
        ).select_related('user', 'provider', 'price_range')
    else:
        queryset = ServiceRequest.objects.filter(
            user=user
        ).select_related('user', 'provider', 'price_range')
    
    # Apply filters if provided
    if filters:
        # Status filter
        status = filters.get('status')
        if status and status in ['pending', 'accepted', 'declined']:
            queryset = queryset.filter(status=status)
        
        # Service type (provider_name) filter
        service_type = filters.get('service_type')
        if service_type:
            queryset = queryset.filter(
                provider_name__icontains=service_type
            )
        
        # Urgent filter
        urgent = filters.get('urgent')
        if urgent and urgent.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(urgent=True)
        
        # Date range filters
        date_from = filters.get('date_from')
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from)
                queryset = queryset.filter(created_at__gte=from_date)
            except (ValueError, TypeError):
                pass
        
        date_to = filters.get('date_to')
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to)
                # Add one day to include the entire to_date
                to_date = to_date.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__lte=to_date)
            except (ValueError, TypeError):
                pass
    
    # Limit to reasonable number of records
    queryset = queryset[:1000]
    
    return queryset


def format_request_for_export(service_request, include_distance=False, distance=None):
    """
    Format a service request object for export.
    
    Args:
        service_request: ServiceRequest instance
        include_distance: Whether to include calculated distance
        distance: Pre-calculated distance (optional)
    
    Returns:
        Dictionary with formatted request data
    """
    price_range_label = ''
    if service_request.price_range:
        price_range_label = service_request.price_range.label
    
    return {
        'request_id': service_request.id,
        'service_type': service_request.provider_name,
        'user_name': service_request.user.get_full_name() or service_request.user.username,
        'provider_name': service_request.provider.get_full_name() if service_request.provider else 'N/A',
        'status': service_request.get_status_display(),
        'date_created': service_request.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'distance': distance if distance is not None else '',
        'price_range': price_range_label,
        'urgent': 'Yes' if service_request.urgent else 'No',
        'description': service_request.description[:200],  # Truncate for export
    }


def generate_csv_export(requests_list):
    """
    Generate CSV content from a list of service requests.
    
    Args:
        requests_list: List of ServiceRequest objects
    
    Returns:
        io.StringIO object containing CSV data
    """
    output = io.StringIO()
    
    fieldnames = [
        'Request ID',
        'Service Type',
        'User Name',
        'Provider Name',
        'Status',
        'Date Created',
        'Distance (miles)',
        'Price Range',
        'Urgent',
        'Description'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for service_request in requests_list:
        formatted_request = format_request_for_export(service_request)
        row = {
            'Request ID': formatted_request['request_id'],
            'Service Type': formatted_request['service_type'],
            'User Name': formatted_request['user_name'],
            'Provider Name': formatted_request['provider_name'],
            'Status': formatted_request['status'],
            'Date Created': formatted_request['date_created'],
            'Distance (miles)': formatted_request['distance'],
            'Price Range': formatted_request['price_range'],
            'Urgent': formatted_request['urgent'],
            'Description': formatted_request['description'],
        }
        writer.writerow(row)
    
    output.seek(0)
    return output


def generate_pdf_export_html(requests_list, export_timestamp=None):
    """
    Generate HTML content for PDF conversion.
    
    Args:
        requests_list: List of ServiceRequest objects
        export_timestamp: DateTime for the export
    
    Returns:
        HTML string ready for PDF conversion
    """
    if export_timestamp is None:
        export_timestamp = timezone.now()
    
    # Calculate summary statistics
    total_requests = len(requests_list)
    status_counts = {}
    for req in requests_list:
        status = req.get_status_display()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                font-size: 28px;
                margin-bottom: 5px;
            }}
            
            .header p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .summary {{
                background: #f8f9fa;
                padding: 20px 30px;
                margin-bottom: 30px;
                border-radius: 5px;
            }}
            
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin-top: 15px;
            }}
            
            .summary-item {{
                background: white;
                padding: 15px;
                border-radius: 3px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            .summary-item-label {{
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            
            .summary-item-value {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            
            table th {{
                background-color: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                font-size: 12px;
            }}
            
            table td {{
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 11px;
            }}
            
            table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            
            .status-pending {{
                background: #fff3cd;
                color: #856404;
                padding: 3px 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
            
            .status-accepted {{
                background: #d4edda;
                color: #155724;
                padding: 3px 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
            
            .status-declined {{
                background: #f8d7da;
                color: #721c24;
                padding: 3px 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                border-top: 1px solid #e0e0e0;
                font-size: 11px;
                color: #666;
                margin-top: 40px;
            }}
            
            .urgent-badge {{
                background: #ff6b6b;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Service Requests Export</h1>
            <p>Generated on {export_timestamp.strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2 style="font-size: 16px; margin-bottom: 15px; color: #333;">Summary Statistics</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-item-label">Total Requests</div>
                    <div class="summary-item-value">{total_requests}</div>
                </div>
    """
    
    # Add status counts to summary
    for status, count in status_counts.items():
        html_content += f"""
                <div class="summary-item">
                    <div class="summary-item-label">{status}</div>
                    <div class="summary-item-value">{count}</div>
                </div>
        """
    
    html_content += """
            </div>
        </div>
        
        <div style="padding: 0 30px;">
            <h2 style="font-size: 16px; margin-bottom: 15px; color: #333;">Requests Detail</h2>
            <table>
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Service Type</th>
                        <th>User Name</th>
                        <th>Provider</th>
                        <th>Status</th>
                        <th>Date Created</th>
                        <th>Price Range</th>
                        <th>Urgent</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add request rows
    for service_request in requests_list:
        formatted = format_request_for_export(service_request)
        status_class = f"status-{service_request.status}"
        urgent_html = '<span class="urgent-badge">URGENT</span>' if service_request.urgent else ''
        
        html_content += f"""
                    <tr>
                        <td>{formatted['request_id']}</td>
                        <td>{formatted['service_type']}</td>
                        <td>{formatted['user_name']}</td>
                        <td>{formatted['provider_name']}</td>
                        <td><span class="{status_class}">{formatted['status']}</span></td>
                        <td>{formatted['date_created']}</td>
                        <td>{formatted['price_range']}</td>
                        <td>{urgent_html}</td>
                        <td>{formatted['description']}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>This report was automatically generated. For more information, please contact support.</p>
        </div>
    </body>
    </html>
    """
    
    return html_content


def get_export_filename(format_type, timestamp=None):
    """
    Generate a filename for exported data.
    
    Args:
        format_type: 'csv' or 'pdf'
        timestamp: DateTime object (uses current time if not provided)
    
    Returns:
        Filename string
    """
    if timestamp is None:
        timestamp = timezone.now()
    
    date_str = timestamp.strftime('%Y-%m-%d')
    return f"service_requests_{date_str}.{format_type}"
