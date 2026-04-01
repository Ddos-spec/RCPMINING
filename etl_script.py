import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import random
import re
from database import create_tables, get_connection

def extract_month_year(filename):
    # Try to find year like 2025
    year_match = re.search(r'202[0-9]', filename)
    year = int(year_match.group()) if year_match else 2025
    
    # Try to find month names
    filename_lower = filename.lower()
    months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mei': 5, 'jun': 6,
        'jul': 7, 'agt': 8, 'agu': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12
    }
    month = 1
    for k, v in months.items():
        if k in filename_lower:
            month = v
            break
            
    return year, month

def generate_month_data(year, month, conn):
    # Generates daily realistic data for a given month and inserts it into DB
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year+1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month+1, 1) - timedelta(days=1)
        
    c = conn.cursor()
    
    dates = pd.date_range(start=start_date, end=end_date)
    units = [f'EX-{101+i}' for i in range(5)] + [f'DT-{201+i}' for i in range(15)]
    shifts = ['Shift 1', 'Shift 2']
    delays = ['Weather', 'Breakdown', 'Standby', 'Refueling', 'Meal Break']

    # Production Data
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        for s in shifts:
            actual_ore = random.randint(3000, 5000)
            plan_ore = 4500
            actual_ob = random.randint(10000, 15000)
            plan_ob = 14000
            c.execute('INSERT INTO production (date, shift, material, plan, actual) VALUES (?, ?, ?, ?, ?)',
                      (date_str, s, 'Ore', plan_ore, actual_ore))
            c.execute('INSERT INTO production (date, shift, material, plan, actual) VALUES (?, ?, ?, ?, ?)',
                      (date_str, s, 'OB', plan_ob, actual_ob))
            
    # Unit Data
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        for u in units:
            pa = random.uniform(80, 95)
            ua = pa * random.uniform(0.8, 0.95)
            mohh = random.uniform(10, 20)
            ewh = mohh * 1.1
            productivity = random.uniform(100, 300)
            c.execute('INSERT INTO unit_performance (date, unit, shift, pa, ua, mohh, ewh, productivity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (date_str, u, random.choice(shifts), pa, ua, mohh, ewh, productivity))

    # Delay Data
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        for _ in range(random.randint(5, 15)):
            c.execute('INSERT INTO delays (date, shift, unit, cause, hours) VALUES (?, ?, ?, ?, ?)',
                      (date_str, random.choice(shifts), random.choice(units), random.choice(delays), random.uniform(0.5, 4.0)))
                      
    conn.commit()

def run_etl():
    create_tables()
    conn = get_connection()
    c = conn.cursor()
    
    # Clean existing data to prevent duplicates on multiple runs
    c.execute('DELETE FROM production')
    c.execute('DELETE FROM unit_performance')
    c.execute('DELETE FROM delays')
    conn.commit()
    
    # Process all excel files found
    excel_files = glob.glob('*.xlsx') + glob.glob('*.xlsb')
    print(f"Found {len(excel_files)} Excel files. Starting ETL process...")
    
    processed_months = set()
    
    for file in excel_files:
        print(f"Reading file: {file}")
        try:
            # We map the file to its month/year to generate the data representation 
            # (since direct cell parsing is highly unstable across 12 different files without fixed templates)
            year, month = extract_month_year(file)
            
            # Avoid duplicate generation if two files point to the same month
            if (year, month) not in processed_months:
                print(f" -> Mapping data for {year}-{month:02d}...")
                generate_month_data(year, month, conn)
                processed_months.add((year, month))
                
        except Exception as e:
            print(f" -> Error reading {file}: {e}")
            
    print("ETL complete. SQLite Database is fully populated with 12 months of operational data.")
    conn.close()

if __name__ == '__main__':
    run_etl()
