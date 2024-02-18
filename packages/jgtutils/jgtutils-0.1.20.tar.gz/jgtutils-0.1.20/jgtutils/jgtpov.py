from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import tlid

def calculate_start_datetime(end_datetime, timeframe, periods):
  # Parse end_datetime string into datetime object
  end_datetime = parse(end_datetime)
  
  # Check if timeframe is in hours
  if timeframe.startswith('H'):
    # Convert timeframe from hours to minutes
    timeframe_minutes = int(timeframe[1:]) * 60
  elif timeframe.startswith('D'):
    # Convert timeframe from days to minutes
    timeframe_days = int(timeframe[1:])
    # Calculate start datetime
    start_datetime = end_datetime - timedelta(days=timeframe_days*periods)
  elif timeframe.startswith('W'):
    # Convert timeframe from weeks to days
    timeframe_weeks = int(timeframe[1:])
    # Calculate start datetime
    start_datetime = end_datetime - timedelta(weeks=timeframe_weeks*periods)
  elif timeframe.startswith('M'):
    # Convert timeframe from months
    timeframe_months = int(timeframe[1:])
    # Calculate start datetime
    start_datetime = end_datetime - relativedelta(months=timeframe_months*periods)
  elif timeframe.startswith('m'):
    # Convert timeframe from minutes
    timeframe_minutes = int(timeframe[1:])
  else:
    # Assume timeframe is already in minutes
    timeframe_minutes = int(timeframe)
  
  # Convert timeframe from minutes to seconds
  timeframe_seconds = timeframe_minutes * 60
  # Calculate total seconds for all periods
  total_seconds = timeframe_seconds * periods
  # Calculate start datetime
  start_datetime = end_datetime - timedelta(seconds=total_seconds)
  
  return start_datetime

def calculate_tlid_range(end_datetime, timeframe, periods):
  # Calculate start datetime
  start_datetime = calculate_start_datetime(end_datetime, timeframe, periods)
  
  # Format start and end datetime to tlid format
  start_tlid = tlid.tlid_dt_to_string(start_datetime)
  end_tlid = tlid.tlid_dt_to_string(parse(end_datetime))
  
  # Return tlid range
  return f"{start_tlid}_{end_tlid}"