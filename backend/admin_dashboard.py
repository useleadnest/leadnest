"""
Admin Analytics Dashboard for LeadNest
Provides metrics and insights for business intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from database import get_db, User, Search, Lead, Export
from auth import get_admin_user
from admin_models import AdminDashboardStats, UserStats, TopUser, TopLocation, TopTrade, DailyActivity, RevenueData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get comprehensive admin dashboard statistics
    Requires admin authentication
    """
    try:
        # Date ranges for comparisons
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        yesterday = now - timedelta(days=1)
        
        # User Statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users_30d = db.query(User).filter(User.created_at >= last_30_days).count()
        new_users_7d = db.query(User).filter(User.created_at >= last_7_days).count()
        
        # Search Statistics
        total_searches = db.query(Search).count()
        searches_30d = db.query(Search).filter(Search.created_at >= last_30_days).count()
        searches_7d = db.query(Search).filter(Search.created_at >= last_7_days).count()
        
        # Lead Statistics
        total_leads = db.query(Lead).count()
        leads_30d = db.query(Lead).filter(Lead.created_at >= last_30_days).count()
        enriched_leads = db.query(Lead).filter(Lead.ai_enriched == True).count()
        
        # Export Statistics
        total_exports = db.query(Export).count()
        exports_30d = db.query(Export).filter(Export.created_at >= last_30_days).count()
        completed_exports = db.query(Export).filter(Export.status == 'completed').count()
        
        # Top Users by Activity
        top_users = db.query(
            User.email,
            func.count(Search.id).label('search_count'),
            func.count(Export.id).label('export_count')
        ).outerjoin(Search).outerjoin(Export).group_by(User.id).order_by(
            func.count(Search.id).desc()
        ).limit(10).all()
        
        # Search trends by location
        top_locations = db.query(
            Search.location,
            func.count(Search.id).label('search_count')
        ).filter(
            Search.location.isnot(None),
            Search.created_at >= last_30_days
        ).group_by(Search.location).order_by(
            func.count(Search.id).desc()
        ).limit(10).all()
        
        # Trade type analysis
        top_trades = db.query(
            Search.trade,
            func.count(Search.id).label('search_count'),
            func.avg(func.json_array_length(Search.results)).label('avg_results')
        ).filter(
            Search.trade.isnot(None),
            Search.created_at >= last_30_days
        ).group_by(Search.trade).order_by(
            func.count(Search.id).desc()
        ).limit(10).all()
        
        # Daily activity for last 30 days
        daily_activity = db.execute(text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(CASE WHEN table_name = 'users' THEN 1 END) as new_users,
                COUNT(CASE WHEN table_name = 'searches' THEN 1 END) as searches,
                COUNT(CASE WHEN table_name = 'exports' THEN 1 END) as exports
            FROM (
                SELECT created_at, 'users' as table_name FROM users WHERE created_at >= :date_30d
                UNION ALL
                SELECT created_at, 'searches' as table_name FROM searches WHERE created_at >= :date_30d
                UNION ALL
                SELECT created_at, 'exports' as table_name FROM exports WHERE created_at >= :date_30d
            ) combined
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        """), {"date_30d": last_30_days}).fetchall()
        
        # Revenue metrics (if subscription data exists)
        revenue_data = {
            "total_revenue": 0,
            "monthly_recurring_revenue": 0,
            "active_subscriptions": 0,
            "subscription_breakdown": {}
        }
        
        # Calculate growth rates
        def calculate_growth_rate(current: int, previous: int) -> float:
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100
        
        # Get previous period data for growth calculations
        users_prev_30d = db.query(User).filter(
            User.created_at >= (last_30_days - timedelta(days=30)),
            User.created_at < last_30_days
        ).count()
        
        searches_prev_30d = db.query(Search).filter(
            Search.created_at >= (last_30_days - timedelta(days=30)),
            Search.created_at < last_30_days
        ).count()
        
        return AdminDashboardStats(
            # User metrics
            total_users=total_users,
            active_users=active_users,
            new_users_30d=new_users_30d,
            new_users_7d=new_users_7d,
            user_growth_rate=calculate_growth_rate(new_users_30d, users_prev_30d),
            
            # Search metrics
            total_searches=total_searches,
            searches_30d=searches_30d,
            searches_7d=searches_7d,
            search_growth_rate=calculate_growth_rate(searches_30d, searches_prev_30d),
            
            # Lead metrics
            total_leads=total_leads,
            leads_30d=leads_30d,
            enriched_leads=enriched_leads,
            enrichment_rate=(enriched_leads / total_leads * 100) if total_leads > 0 else 0,
            
            # Export metrics
            total_exports=total_exports,
            exports_30d=exports_30d,
            completed_exports=completed_exports,
            export_success_rate=(completed_exports / total_exports * 100) if total_exports > 0 else 0,
            
            # Top lists
            top_users=[{
                "email": user.email,
                "search_count": user.search_count,
                "export_count": user.export_count
            } for user in top_users],
            
            top_locations=[{
                "location": loc.location,
                "search_count": loc.search_count
            } for loc in top_locations],
            
            top_trades=[{
                "trade": trade.trade,
                "search_count": trade.search_count,
                "avg_results": float(trade.avg_results) if trade.avg_results else 0
            } for trade in top_trades],
            
            # Activity trends
            daily_activity=[{
                "date": str(day.date),
                "new_users": day.new_users,
                "searches": day.searches,
                "exports": day.exports
            } for day in daily_activity],
            
            # Revenue data
            revenue_data=revenue_data
        )
        
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )

@router.get("/users", response_model=List[UserStats])
async def get_user_analytics(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get detailed user analytics with activity metrics"""
    
    users = db.query(
        User.id,
        User.email,
        User.created_at,
        User.is_active,
        User.is_admin,
        func.count(Search.id).label('total_searches'),
        func.count(Export.id).label('total_exports'),
        func.max(Search.created_at).label('last_search'),
        func.max(Export.created_at).label('last_export')
    ).outerjoin(Search).outerjoin(Export).group_by(
        User.id
    ).order_by(
        User.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [UserStats(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        is_active=user.is_active,
        is_admin=user.is_admin,
        total_searches=user.total_searches,
        total_exports=user.total_exports,
        last_search=user.last_search,
        last_export=user.last_export
    ) for user in users]

@router.get("/searches/analytics")
async def get_search_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get search pattern analytics"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Search volume by hour
    hourly_volume = db.execute(text("""
        SELECT 
            EXTRACT(hour FROM created_at) as hour,
            COUNT(*) as search_count
        FROM searches 
        WHERE created_at >= :start_date
        GROUP BY EXTRACT(hour FROM created_at)
        ORDER BY hour
    """), {"start_date": start_date}).fetchall()
    
    # Search success rate by trade
    trade_success = db.execute(text("""
        SELECT 
            trade,
            COUNT(*) as total_searches,
            AVG(CASE WHEN json_array_length(results) > 0 THEN 1 ELSE 0 END) as success_rate
        FROM searches 
        WHERE created_at >= :start_date AND trade IS NOT NULL
        GROUP BY trade
        ORDER BY total_searches DESC
    """), {"start_date": start_date}).fetchall()
    
    return {
        "hourly_volume": [{"hour": h.hour, "count": h.search_count} for h in hourly_volume],
        "trade_success": [{"trade": t.trade, "total": t.total_searches, "success_rate": float(t.success_rate)} for t in trade_success]
    }

@router.get("/exports/analytics")
async def get_export_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get export usage analytics"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Export volume and success rates
    export_stats = db.execute(text("""
        SELECT 
            status,
            COUNT(*) as count,
            AVG(lead_count) as avg_leads,
            SUM(lead_count) as total_leads
        FROM exports 
        WHERE created_at >= :start_date
        GROUP BY status
    """), {"start_date": start_date}).fetchall()
    
    # Most popular export sizes
    size_distribution = db.execute(text("""
        SELECT 
            CASE 
                WHEN lead_count <= 10 THEN '1-10'
                WHEN lead_count <= 50 THEN '11-50'
                WHEN lead_count <= 100 THEN '51-100'
                WHEN lead_count <= 500 THEN '101-500'
                ELSE '500+'
            END as size_range,
            COUNT(*) as count
        FROM exports 
        WHERE created_at >= :start_date AND status = 'completed'
        GROUP BY size_range
        ORDER BY count DESC
    """), {"start_date": start_date}).fetchall()
    
    return {
        "export_stats": [{"status": s.status, "count": s.count, "avg_leads": float(s.avg_leads), "total_leads": s.total_leads} for s in export_stats],
        "size_distribution": [{"range": s.size_range, "count": s.count} for s in size_distribution]
    }

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Toggle user active status (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    logger.info(f"Admin {current_user.email} {'activated' if user.is_active else 'deactivated'} user {user.email}")
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_email": user.email,
        "is_active": user.is_active
    }

@router.delete("/searches/{search_id}")
async def delete_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a search and associated leads (admin only)"""
    
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Delete associated leads
    lead_count = db.query(Lead).filter(Lead.search_id == search_id).count()
    db.query(Lead).filter(Lead.search_id == search_id).delete()
    
    # Delete search
    db.delete(search)
    db.commit()
    
    logger.info(f"Admin {current_user.email} deleted search {search_id} with {lead_count} leads")
    
    return {
        "message": "Search and associated leads deleted successfully",
        "deleted_leads": lead_count
    }

@router.get("/system/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get system health metrics"""
    
    try:
        # Database health
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        
        # Table sizes
        table_sizes = db.execute(text("""
            SELECT 
                'users' as table_name, COUNT(*) as row_count FROM users
            UNION ALL
            SELECT 
                'searches' as table_name, COUNT(*) as row_count FROM searches
            UNION ALL
            SELECT 
                'leads' as table_name, COUNT(*) as row_count FROM leads
            UNION ALL
            SELECT 
                'exports' as table_name, COUNT(*) as row_count FROM exports
        """)).fetchall()
        
        # Recent activity
        recent_activity = db.execute(text("""
            SELECT COUNT(*) as count FROM (
                SELECT created_at FROM users WHERE created_at >= NOW() - INTERVAL '1 hour'
                UNION ALL
                SELECT created_at FROM searches WHERE created_at >= NOW() - INTERVAL '1 hour'
                UNION ALL
                SELECT created_at FROM exports WHERE created_at >= NOW() - INTERVAL '1 hour'
            ) recent
        """)).fetchone()
        
        return {
            "database_status": db_status,
            "table_sizes": [{"table": t.table_name, "rows": t.row_count} for t in table_sizes],
            "recent_activity_1h": recent_activity.count if recent_activity else 0,
            "system_time": datetime.utcnow().isoformat(),
            "uptime": "healthy"  # Could be enhanced with actual uptime tracking
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System health check failed"
        )
