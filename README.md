BharatBricks UI Documentation

Frontend UI Overview for BharatBricks Retail Intelligence System
Version 1.0 | April 2026

Overview

This document describes the frontend user interface developed for BharatBricks, including:

Onboarding (Login) Flow
Main Application Dashboard

The UI is designed for small retail shop owners, focusing on simplicity, speed, and mobile-first usability.

1. Onboarding / Login Flow
Purpose

The onboarding flow collects essential shop and owner data to initialize the system and personalize AI-driven insights.

Key Features
1.1 Phone Verification
Mobile number input (India format)
OTP-based authentication (demo-enabled)
Ensures unique user identity
1.2 Owner Details
Owner name input
Language selection:
Hindi (hi)
English (en)
1.3 Shop Identity
Shop name input
Shop type selection:
Kirana / Grocery
Pharma
Food / Tiffin
Textiles
Electronics
Jewellery
1.4 Location Information
Village / City
District
State (dropdown)
Area type:
Metro
Urban
Semi-urban
Rural
Supplier lead time selection
1.5 Business Scale Inputs
Monthly revenue
Daily transactions
Average bill value
Number of products
Supplier count
UPI / digital payment usage
1.6 Inventory Setup

Two options:

Option 1: File Upload

CSV / Excel upload
Expected columns:
product_name
qty
price_per_unit

Option 2: Cold Start Mode

RAG-based prior (instant insights)
Learning mode (7-day data collection before insights)
1.7 Completion Summary
Displays all collected data
Confirms onboarding completion
Launch button redirects to main application
Data Captured
{
  "phone": "",
  "name": "",
  "language": "",
  "shopName": "",
  "shopType": "",
  "location": "",
  "district": "",
  "state": "",
  "areaType": "",
  "leadTime": "",
  "revenue": "",
  "transactions": "",
  "avgBill": "",
  "products": "",
  "suppliers": "",
  "upi": "",
  "coldStart": "",
  "stockFile": ""
}
2. Main Application UI
Purpose

The main dashboard enables:

Daily sales logging
Order tracking
Billing and payment handling
AI-powered insights
2.1 Main Dashboard
Features
Shop greeting and name display
Daily sales summary:
Total revenue
Number of orders
Location
Action buttons:
Log Sale
AI Dashboard
Order list display
2.2 Sales Logging Interface
Features
Product search functionality
Quick-add product chips
Cart system:
Add/remove items
Quantity adjustment
Real-time total calculation
Confirmation button to generate bill
2.3 Billing System
Features
Order summary view
Itemized billing
Total amount display
Payment methods:
Cash
UPI
Credit (Udhar)
Final confirmation action
2.4 Order Tracking
Displays recent orders
Includes:
Order ID
Time
Number of items
Payment type
Total value
2.5 AI Dashboard
Sections

Urgent

Low stock alerts
Reorder recommendations

Weekly

Weekly stocking plan
Sales trend visualization

Seasonal

Festival-based demand insights
Weather-based product trends

Summary

Monthly performance metrics
AI-generated recommendations
3. UI Architecture
Technology Stack
HTML5
CSS3 (custom styling, mobile-first)
Vanilla JavaScript
Google Fonts:
Baloo 2
Noto Sans
Design Principles
Mobile-first layout (390px width simulation)
Minimal input friction
Hindi-first usability with bilingual support
Fast interactions (no heavy frameworks)
Visual clarity using cards and pills
4. State Management
Onboarding State

All onboarding data is stored in a single object:

const D = {};
Main App State
let cart = {};
let orders = [];
let orderCounter = 1001;
let selectedPayment = 'cash';
5. Navigation Flow
Onboarding
Phone → OTP → Name → Shop → Location → Business → Stock → Done
Main App
Dashboard
   ├── Log Sale
   │     ├── Cart
   │     └── Bill
   └── AI Dashboard
6. Integration Points
Backend Integration (Planned)
Databricks Delta Tables
REST API for:
Shop profile creation
Sales logging
Forecast retrieval

Example:

POST /api/2.0/sql/statements
INSERT INTO workspace.default.shop_profiles
7. Demo Behavior
OTP accepts any 4 digits
File upload is simulated
Data stored in memory
Alerts and AI insights are mock-generated
8. Future Improvements
Real OTP integration
Actual file upload and parsing
Backend persistence
Multi-language expansion
Offline-first capability
Native mobile application
Conclusion

The BharatBricks UI provides a complete, lightweight interface for small retailers to:

Digitally log sales
Track business performance
Receive AI-driven recommendations

It is optimized for usability in low-tech environments while remaining extensible for advanced backend intelligence.
