"""
Pydantic models for admin dashboard analytics
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserStats(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool
    is_admin: bool
    total_searches: int
    total_exports: int
    last_search: Optional[datetime] = None
    last_export: Optional[datetime] = None

class TopUser(BaseModel):
    email: str
    search_count: int
    export_count: int

class TopLocation(BaseModel):
    location: str
    search_count: int

class TopTrade(BaseModel):
    trade: str
    search_count: int
    avg_results: float

class DailyActivity(BaseModel):
    date: str
    new_users: int
    searches: int
    exports: int

class RevenueData(BaseModel):
    total_revenue: float
    monthly_recurring_revenue: float
    active_subscriptions: int
    subscription_breakdown: Dict[str, Any]

class AdminDashboardStats(BaseModel):
    # User metrics
    total_users: int
    active_users: int
    new_users_30d: int
    new_users_7d: int
    user_growth_rate: float
    
    # Search metrics
    total_searches: int
    searches_30d: int
    searches_7d: int
    search_growth_rate: float
    
    # Lead metrics
    total_leads: int
    leads_30d: int
    enriched_leads: int
    enrichment_rate: float
    
    # Export metrics
    total_exports: int
    exports_30d: int
    completed_exports: int
    export_success_rate: float
    
    # Top lists
    top_users: List[TopUser]
    top_locations: List[TopLocation]
    top_trades: List[TopTrade]
    
    # Trends
    daily_activity: List[DailyActivity]
    
    # Revenue
    revenue_data: RevenueData

class SearchStats(BaseModel):
    total_searches: int
    searches_today: int
    avg_results_per_search: float
    most_searched_location: str
    most_searched_trade: str

class ExportStats(BaseModel):
    total_exports: int
    exports_today: int
    total_leads_exported: int
    avg_leads_per_export: float
    success_rate: float

class SubscriptionStats(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    monthly_revenue: float
    churn_rate: float
    plan_breakdown: Dict[str, int]

class SystemHealth(BaseModel):
    database_status: str
    table_sizes: List[Dict[str, Any]]
    recent_activity_1h: int
    system_time: str
    uptime: str
