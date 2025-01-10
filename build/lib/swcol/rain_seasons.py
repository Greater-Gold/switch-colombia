def year(year, mes):
    if mes in ['December']: return year + 1
    else: return year

# Determe Rain Season (Colombia)
def quarter(mes):
    if mes in ['March', 'April', 'May']: return 'Q2'
    elif mes in ['June', 'July', 'August']: return 'Q3'
    elif mes in ['September', 'October', 'November']: return 'Q4'
    else: return 'Q1'
    
def day(day):
    if day == 'Sunday': return 'holidays'
    else: return 'labor'

# Format hour to HH:mm:ss
def extract_hour(hour_string):
    hour = hour_string[-2:]
    if hour == '24':
        return f"00:00:00"
    else:
        return f"{hour}:00:00"

import pandas as pd
def format_hours(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['timestamp'] = df['Date'].apply(\
    lambda x: f"{year(x.year,x.strftime('%B'))}_{quarter(x.strftime('%B'))}_{day(x.day_name())}_{x.hour}h")

    return df

def format_year(df, year):
    df['Date'] = pd.to_datetime(df['Date'])
    df['timestamp'] = df['Date'].apply(\
    lambda x: f"{year}_{quarter(x.strftime('%B'))}_{day(x.day_name())}_{x.hour}h")
    return df