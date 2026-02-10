from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Any
from app.models.expense import Expense
from app.models.category import Category


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_expense_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive expense analytics with multiple time windows
        Returns data for 3 months, 6 months, 1 year, and 3 years
        """
        now = datetime.now()

        # Calculate date boundaries
        three_months_ago = now - relativedelta(months=3)
        six_months_ago = now - relativedelta(months=6)
        one_year_ago = now - relativedelta(years=1)
        three_years_ago = now - relativedelta(years=3)

        return {
            "three_months": self._get_period_analytics(user_id, three_months_ago, now),
            "six_months": self._get_period_analytics(user_id, six_months_ago, now),
            "one_year": self._get_period_analytics(user_id, one_year_ago, now),
            "three_years": self._get_period_analytics(user_id, three_years_ago, now),
            "all_time": self._get_all_time_analytics(user_id)
        }

    def get_expense_analysis_detail(self, user_id: int) -> Dict[str, Any]:
        """Get detailed expense analytics for the deep-dive page."""
        now = datetime.now()
        month_window_start = (now.replace(day=1) - relativedelta(months=23))
        category_month_start = (now.replace(day=1) - relativedelta(months=11))
        year_window_start = datetime(now.year - 3, 1, 1)

        base_filters = and_(Expense.user_id == user_id, Expense.status == True)

        totals_query = self.db.query(
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count'),
            func.min(Expense.date).label('first_expense'),
            func.max(Expense.date).label('last_expense')
        ).filter(base_filters).first()

        total_amount = float(totals_query.total or 0)
        expense_count = totals_query.count or 0
        first_expense = totals_query.first_expense
        last_expense = totals_query.last_expense

        months_of_data = 0
        if first_expense and last_expense:
            months_of_data = (
                (last_expense.year - first_expense.year) * 12
                + last_expense.month - first_expense.month + 1
            )

        avg_monthly = total_amount / months_of_data if months_of_data > 0 else 0
        avg_transaction = total_amount / expense_count if expense_count > 0 else 0

        yearly_totals = self.db.query(
            extract('year', Expense.date).label('year'),
            func.sum(Expense.amount).label('total')
        ).filter(base_filters).group_by(
            extract('year', Expense.date)
        ).order_by(
            extract('year', Expense.date)
        ).all()

        monthly_totals = self.db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                base_filters,
                Expense.date >= month_window_start.date(),
                Expense.date <= now.date()
            )
        ).group_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).order_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).all()

        yearly_totals_data = [{"year": int(t.year), "total": float(t.total)} for t in yearly_totals]
        monthly_totals_data = [{"year": int(t.year), "month": int(t.month), "total": float(t.total)} for t in monthly_totals]

        peak_year = max(yearly_totals_data, key=lambda item: item["total"]) if yearly_totals_data else None
        peak_month = max(monthly_totals_data, key=lambda item: item["total"]) if monthly_totals_data else None

        current_month_key = now.year * 12 + now.month
        last_12_start = current_month_key - 11
        prev_12_start = current_month_key - 23
        prev_12_end = current_month_key - 12

        last_12_total = 0.0
        prev_12_total = 0.0
        for item in monthly_totals_data:
            month_key = item["year"] * 12 + item["month"]
            if last_12_start <= month_key <= current_month_key:
                last_12_total += item["total"]
            elif prev_12_start <= month_key <= prev_12_end:
                prev_12_total += item["total"]

        yoy_change_pct = None
        if prev_12_total > 0:
            yoy_change_pct = round(((last_12_total - prev_12_total) / prev_12_total) * 100, 2)

        category_totals = self.db.query(
            Category.id,
            Category.name,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            and_(
                base_filters,
                Category.user_id == user_id
            )
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.sum(Expense.amount).desc()
        ).all()

        category_yearly = self.db.query(
            Category.id,
            Category.name,
            extract('year', Expense.date).label('year'),
            func.sum(Expense.amount).label('total')
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            and_(
                base_filters,
                Category.user_id == user_id,
                Expense.date >= year_window_start.date()
            )
        ).group_by(
            Category.id, Category.name, extract('year', Expense.date)
        ).order_by(
            Category.name, extract('year', Expense.date)
        ).all()

        category_monthly = self.db.query(
            Category.id,
            Category.name,
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            and_(
                base_filters,
                Category.user_id == user_id,
                Expense.date >= month_window_start.date()
            )
        ).group_by(
            Category.id, Category.name, extract('year', Expense.date), extract('month', Expense.date)
        ).order_by(
            Category.name, extract('year', Expense.date), extract('month', Expense.date)
        ).all()

        category_yearly_map = {}
        for item in category_yearly:
            category_yearly_map.setdefault(str(item.id), []).append({
                "year": int(item.year),
                "total": float(item.total)
            })

        category_monthly_map = {}
        category_last_12 = {}
        category_prev_12 = {}
        for item in category_monthly:
            month_key = int(item.year) * 12 + int(item.month)
            category_id = str(item.id)

            if month_key >= last_12_start:
                category_monthly_map.setdefault(category_id, []).append({
                    "year": int(item.year),
                    "month": int(item.month),
                    "total": float(item.total)
                })

            if last_12_start <= month_key <= current_month_key:
                category_last_12[category_id] = category_last_12.get(category_id, 0.0) + float(item.total)
            elif prev_12_start <= month_key <= prev_12_end:
                category_prev_12[category_id] = category_prev_12.get(category_id, 0.0) + float(item.total)

        categories_data = []
        for category in category_totals:
            category_id = str(category.id)
            last_12 = category_last_12.get(category_id, 0.0)
            prev_12 = category_prev_12.get(category_id, 0.0)
            yoy_change = None
            if prev_12 > 0:
                yoy_change = round(((last_12 - prev_12) / prev_12) * 100, 2)

            categories_data.append({
                "id": category.id,
                "name": category.name,
                "total_amount": float(category.total or 0),
                "expense_count": category.count or 0,
                "percentage": (float(category.total) / total_amount * 100) if total_amount > 0 else 0,
                "last_12_total": last_12,
                "prev_12_total": prev_12,
                "yoy_change": yoy_change,
                "avg_monthly_12": last_12 / 12 if last_12 > 0 else 0
            })

        return {
            "summary": {
                "total_amount": total_amount,
                "expense_count": expense_count,
                "avg_monthly": avg_monthly,
                "avg_transaction": avg_transaction,
                "months_of_data": months_of_data,
                "first_expense_date": first_expense.isoformat() if first_expense else None,
                "last_expense_date": last_expense.isoformat() if last_expense else None,
                "peak_year": peak_year,
                "peak_month": peak_month,
                "last_12_total": last_12_total,
                "prev_12_total": prev_12_total,
                "yoy_change_pct": yoy_change_pct
            },
            "yearly_totals": yearly_totals_data,
            "monthly_totals": monthly_totals_data,
            "categories": categories_data,
            "category_yearly": category_yearly_map,
            "category_monthly": category_monthly_map
        }

    def _get_period_analytics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics for a specific time period"""
        window_start = start_date.replace(day=1)

        # Total expenses and count
        total_query = self.db.query(
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.date >= window_start.date(),
                Expense.date <= end_date.date(),
                Expense.status == True
            )
        ).first()

        total_amount = float(total_query.total or 0)
        expense_count = total_query.count or 0

        # Average monthly spending
        months_diff = max(1, (end_date.year - window_start.year) * 12 + end_date.month - window_start.month)
        avg_monthly = total_amount / months_diff if months_diff > 0 else 0

        # Top categories
        top_categories = self.db.query(
            Category.name,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.date >= window_start.date(),
                Expense.date <= end_date.date(),
                Expense.status == True
            )
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.sum(Expense.amount).desc()
        ).limit(5).all()

        # Monthly trend (last N months)
        monthly_trend = self.db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.date >= window_start.date(),
                Expense.date <= end_date.date(),
                Expense.status == True
            )
        ).group_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).order_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).all()

        # Yearly trend with additional details
        yearly_trend = self.db.query(
            extract('year', Expense.date).label('year'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.date >= window_start.date(),
                Expense.date <= end_date.date(),
                Expense.status == True
            )
        ).group_by(
            extract('year', Expense.date)
        ).order_by(
            extract('year', Expense.date)
        ).all()

        # Get detailed yearly data with months count and top categories
        yearly_trend_data = []
        for year_data in yearly_trend:
            year = int(year_data.year)

            # Count unique months in this year
            months_count = self.db.query(
                func.count(func.distinct(extract('month', Expense.date)))
            ).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('year', Expense.date) == year,
                    Expense.date >= window_start.date(),
                    Expense.date <= end_date.date(),
                    Expense.status == True
                )
            ).scalar()

            # Get top 3 categories for this year
            top_cats = self.db.query(
                Category.name,
                func.sum(Expense.amount).label('total')
            ).join(
                Expense, Expense.category_id == Category.id
            ).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('year', Expense.date) == year,
                    Expense.date >= window_start.date(),
                    Expense.date <= end_date.date(),
                    Expense.status == True
                )
            ).group_by(
                Category.id, Category.name
            ).order_by(
                func.sum(Expense.amount).desc()
            ).limit(3).all()

            yearly_total = float(year_data.total)
            yearly_trend_data.append({
                "year": year,
                "total": yearly_total,
                "months_count": months_count or 0,
                "top_categories": [
                    {
                        "name": cat.name,
                        "total": float(cat.total),
                        "percentage": (float(cat.total) / yearly_total * 100) if yearly_total > 0 else 0
                    }
                    for cat in top_cats
                ]
            })

        # Calculate growth rate
        trend_data = [{"year": int(t.year), "month": int(t.month), "total": float(t.total)} for t in monthly_trend]
        growth_rate = self._calculate_growth_rate(trend_data)

        yearly_growth_rate = self._calculate_yearly_growth_rate(yearly_trend_data)

        return {
            "total_amount": total_amount,
            "expense_count": expense_count,
            "avg_monthly": avg_monthly,
            "top_categories": [
                {
                    "name": cat.name,
                    "total": float(cat.total),
                    "count": cat.count,
                    "percentage": (float(cat.total) / total_amount * 100) if total_amount > 0 else 0
                }
                for cat in top_categories
            ],
            "monthly_trend": trend_data,
            "yearly_trend": yearly_trend_data,
            "growth_rate": growth_rate,
            "yearly_growth_rate": yearly_growth_rate
        }

    def _get_all_time_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get all-time analytics"""

        # Total and count
        total_query = self.db.query(
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count'),
            func.min(Expense.date).label('first_expense'),
            func.max(Expense.date).label('last_expense')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.status == True
            )
        ).first()

        total_amount = float(total_query.total or 0)
        expense_count = total_query.count or 0
        first_expense = total_query.first_expense
        last_expense = total_query.last_expense

        # Calculate months of data
        months_of_data = 0
        if first_expense and last_expense:
            months_of_data = (last_expense.year - first_expense.year) * 12 + last_expense.month - first_expense.month + 1

        avg_monthly = total_amount / months_of_data if months_of_data > 0 else 0

        # Top categories all time
        top_categories = self.db.query(
            Category.name,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.status == True
            )
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.sum(Expense.amount).desc()
        ).limit(10).all()

        # Monthly trend (all time)
        monthly_trend = self.db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.status == True
            )
        ).group_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).order_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).all()

        # Yearly trend (all time)
        yearly_trend = self.db.query(
            extract('year', Expense.date).label('year'),
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.user_id == user_id,
                Expense.status == True
            )
        ).group_by(
            extract('year', Expense.date)
        ).order_by(
            extract('year', Expense.date)
        ).all()

        yearly_trend_data = []
        for year_data in yearly_trend:
            year = int(year_data.year)

            months_count = self.db.query(
                func.count(func.distinct(extract('month', Expense.date)))
            ).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('year', Expense.date) == year,
                    Expense.status == True
                )
            ).scalar()

            top_cats = self.db.query(
                Category.name,
                func.sum(Expense.amount).label('total')
            ).join(
                Expense, Expense.category_id == Category.id
            ).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('year', Expense.date) == year,
                    Expense.status == True
                )
            ).group_by(
                Category.id, Category.name
            ).order_by(
                func.sum(Expense.amount).desc()
            ).limit(3).all()

            yearly_total = float(year_data.total)
            yearly_trend_data.append({
                "year": year,
                "total": yearly_total,
                "months_count": months_count or 0,
                "top_categories": [
                    {
                        "name": cat.name,
                        "total": float(cat.total),
                        "percentage": (float(cat.total) / yearly_total * 100) if yearly_total > 0 else 0
                    }
                    for cat in top_cats
                ]
            })

        trend_data = [{"year": int(t.year), "month": int(t.month), "total": float(t.total)} for t in monthly_trend]
        growth_rate = self._calculate_growth_rate(trend_data)
        yearly_growth_rate = self._calculate_yearly_growth_rate(yearly_trend_data)

        return {
            "total_amount": total_amount,
            "expense_count": expense_count,
            "avg_monthly": avg_monthly,
            "months_of_data": months_of_data,
            "first_expense_date": first_expense.isoformat() if first_expense else None,
            "last_expense_date": last_expense.isoformat() if last_expense else None,
            "monthly_trend": trend_data,
            "yearly_trend": yearly_trend_data,
            "growth_rate": growth_rate,
            "yearly_growth_rate": yearly_growth_rate,
            "top_categories": [
                {
                    "name": cat.name,
                    "total": float(cat.total),
                    "count": cat.count,
                    "percentage": (float(cat.total) / total_amount * 100) if total_amount > 0 else 0
                }
                for cat in top_categories
            ]
        }

    def _calculate_growth_rate(self, trend_data: List[Dict]) -> float:
        """Calculate month-over-month growth rate"""
        if len(trend_data) < 2:
            return 0.0

        # Compare last month to previous month
        last_month = trend_data[-1]["total"]
        prev_month = trend_data[-2]["total"]

        if prev_month == 0:
            return 0.0

        growth = ((last_month - prev_month) / prev_month) * 100
        return round(growth, 2)

    def _calculate_yearly_growth_rate(self, yearly_data: List[Dict]) -> float:
        """Calculate year-over-year growth rate"""
        if len(yearly_data) < 2:
            return 0.0

        # Compare last year to previous year
        last_year = yearly_data[-1]["total"]
        prev_year = yearly_data[-2]["total"]

        if prev_year == 0:
            return 0.0

        growth = ((last_year - prev_year) / prev_year) * 100
        return round(growth, 2)
