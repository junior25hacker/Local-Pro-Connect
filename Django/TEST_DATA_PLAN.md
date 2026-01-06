# Comprehensive Test Data Plan

## Overview
This document outlines the test data that will be created for the Django application to support testing of the request list and detail pages.

## Data to be Created

### 1. Price Ranges (5 objects)
- Under $50 (0-50)
- $50-$100 (50-100)
- $100-$250 (100-250)
- $250-$500 (250-500)
- $500+ (500+)

### 2. Regular Users (4 users with UserProfile)
Different NYC zip codes for distance calculation testing:

| Username | Name | Email | Zip Code | City |
|----------|------|-------|----------|------|
| john_miller | John Miller | john.miller@example.com | 10001 | New York |
| sarah_johnson | Sarah Johnson | sarah.johnson@example.com | 10002 | New York |
| mike_chen | Mike Chen | mike.chen@example.com | 11201 | Brooklyn |
| diana_garcia | Diana Garcia | diana.garcia@example.com | 11354 | Forest Hills |

### 3. Service Providers (5 providers with ProviderProfile)
Different service types and locations:

| Username | Company | Service Type | Zip Code | City | Experience | Rating |
|----------|---------|--------------|----------|------|------------|--------|
| plumber_joe | Joe's Plumbing Solutions | Plumbing | 10001 | New York | 15 yrs | 4.8 |
| electrician_tom | Tom's Electric | Electrical | 11201 | Brooklyn | 20 yrs | 4.9 |
| carpenter_alex | Alex's Custom Carpentry | Carpentry | 11354 | Queens | 12 yrs | 4.7 |
| cleaner_maria | Maria's Cleaning Service | Cleaning | 10002 | New York | 8 yrs | 4.6 |
| hvac_dave | Dave's HVAC Solutions | HVAC | 11201 | Queens | 18 yrs | 4.5 |

### 4. Service Requests (10 requests with various statuses)

#### Pending Requests (4)
1. John Miller → Joe's Plumbing (Fix leaky faucet)
2. Mike Chen → Joe's Plumbing (Replace bathroom tiles)
3. Diana Garcia → Tom's Electric (Upgrade electrical panel) - URGENT
4. John Miller → Maria's Cleaning (Office cleaning service)
5. Sarah Johnson → Dave's HVAC (Install new heating system) - URGENT

#### Accepted Requests (3)
1. John Miller → Tom's Electric (Install light fixtures)
2. Sarah Johnson → Maria's Cleaning (Deep clean apartment) - URGENT
3. Mike Chen → Dave's HVAC (AC maintenance)

#### Declined Requests (2)
1. Sarah Johnson → Alex's Carpentry (Custom shelving) - Reason: Distance
2. Diana Garcia → Alex's Carpentry (Repair wooden deck) - Reason: Price too low

## Testing Coverage

### Distance Calculation
- Users in different zip codes (10001, 10002, 11201, 11354)
- Providers in different zip codes
- Declined requests with "distance" reason

### Status Workflow
- Pending requests awaiting provider response
- Accepted requests with timestamps
- Declined requests with reasons and messages

### Service Types
- Plumbing
- Electrical
- Carpentry
- Cleaning
- HVAC

### Price Ranges
- Multiple price ranges for different service types
- Tests for filter and display functionality

## Database Summary After Creation
- Regular Users: 4
- Service Providers: 5
- Service Requests: 10
- Price Ranges: 5
- Total Users (combined): 9
- Status Breakdown: 4 Pending, 3 Accepted, 2 Declined
