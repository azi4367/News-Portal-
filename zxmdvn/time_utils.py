from datetime import datetime

def timeago(dt):
    now = datetime.utcnow()
    diff = now - dt

    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days

    if seconds < 60:
        return f"{seconds} seconds ago"  # ✅ Yeh line change ki gayi
    elif minutes < 60:
        return f"{int(minutes)} minutes ago"
    elif hours < 24:
        return f"{int(hours)} hours ago"
    elif days == 1:
        return "Yesterday"
    elif days < 7:
        return f"{int(days)} days ago"
    else:
        return dt.strftime("%d %b, %I:%M %p")
