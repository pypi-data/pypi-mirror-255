import schedule
import time
import mlflow
import mlflow.pyfunc
from datetime import datetime, timedelta
import pytz
import os

# 'America/New_York'
def get_datetime_now_trade(timezone :str = 'Europe/Madrid', delay_minutes = 15, days_ago = 100):
    
    ny_timezone = pytz.timezone(timezone)
    now_ny = datetime.now(ny_timezone)
    start_date_ny = now_ny - timedelta(days=days_ago)
    start_date_ny = start_date_ny.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date_ny = start_date_ny.strftime('%m/%d/%Y')
    end_date_ny = now_ny - timedelta(minutes=delay_minutes)
    end_date_ny = end_date_ny.strftime('%m/%d/%Y %H:%M')
 
    return start_date_ny, end_date_ny, now_ny