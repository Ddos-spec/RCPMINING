import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_NAME = "tambang.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    # Table Production
    c.execute('''
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            shift TEXT,
            material TEXT,
            plan REAL,
            actual REAL
        )
    ''')
    # Table Unit Performance
    c.execute('''
        CREATE TABLE IF NOT EXISTS unit_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            unit TEXT,
            shift TEXT,
            pa REAL,
            ua REAL,
            mohh REAL,
            ewh REAL,
            productivity REAL
        )
    ''')
    # Table Delays
    c.execute('''
        CREATE TABLE IF NOT EXISTS delays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            shift TEXT,
            unit TEXT,
            cause TEXT,
            hours REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_production(date, shift, material, plan, actual):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO production (date, shift, material, plan, actual) VALUES (?, ?, ?, ?, ?)',
              (date, shift, material, plan, actual))
    conn.commit()
    conn.close()

def insert_unit_performance(date, unit, shift, pa, ua, mohh, ewh, productivity):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO unit_performance (date, unit, shift, pa, ua, mohh, ewh, productivity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (date, unit, shift, pa, ua, mohh, ewh, productivity))
    conn.commit()
    conn.close()

def load_data_to_df(table_name):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df
