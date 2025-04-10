from datetime import datetime, date, timedelta
import calendar

def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """Get the first and last day of a month"""
    first_day = date(year, month, 1)
    _, last_day_num = calendar.monthrange(year, month)
    last_day = date(year, month, last_day_num)
    return first_day, last_day

def get_week_range(dt: date) -> Tuple[date, date]:
    """Get the first and last day of the week for a given date"""
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return start, end

def format_date(dt: date) -> str:
    """Format date as YYYY-MM-DD"""
    return dt.strftime("%Y-%m-%d")

def format_datetime(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM"""
    return dt.strftime("%Y-%m-%d %H:%M")

def get_relative_time(dt: datetime) -> str:
    """Get relative time string (e.g., '2 hours ago')"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"
