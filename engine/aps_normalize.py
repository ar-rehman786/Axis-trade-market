# Normalize & Score - Complete Implementation (Fixed)
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from engine.aps_config import REQUIRED_HEADERS, ENGINE_DIR

def normalize_and_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main normalization and scoring function
    Handles both normalized and raw vendor column names
    """
    
    # Create working columns with consistent names
    # Property Value
    if 'EstValue' in df.columns:
        df['_property_value'] = pd.to_numeric(df['EstValue'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    elif 'property_value' in df.columns:
        df['_property_value'] = pd.to_numeric(df['property_value'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    else:
        df['_property_value'] = 0
    
    # Loan Balance
    if 'TotalLoanBal' in df.columns:
        df['_loan_balance'] = pd.to_numeric(df['TotalLoanBal'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    elif 'loan_balance' in df.columns:
        df['_loan_balance'] = pd.to_numeric(df['loan_balance'].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce')
    else:
        df['_loan_balance'] = 0
    
    # Loan Date
    if 'LastLoanDate' in df.columns:
        df['_loan_date'] = pd.to_datetime(df['LastLoanDate'], errors='coerce')
    elif 'loan_date' in df.columns:
        df['_loan_date'] = pd.to_datetime(df['loan_date'], errors='coerce')
    else:
        df['_loan_date'] = pd.NaT
    
    # Calculate LTV %
    df['LTV %'] = ((df['_loan_balance'] / df['_property_value']) * 100).round(2)
    df['LTV %'] = df['LTV %'].fillna(0).clip(0, 100)
    
    # Calculate Equity %
    df['Equity %'] = (100 - df['LTV %']).round(2)
    
    # Calculate Equity Dollars
    df['Equity_Dollars'] = (df['_property_value'] * (df['Equity %'] / 100)).round(0)
    
    # Calculate Loan Age in Months
    def calculate_months(loan_date):
        if pd.isna(loan_date):
            return 0
        today = datetime.now()
        years_diff = today.year - loan_date.year
        months_diff = today.month - loan_date.month
        total_months = years_diff * 12 + months_diff
        return max(0, total_months)
    
    df['Loan_Age_Mo'] = df['_loan_date'].apply(calculate_months)
    
    # Calculate APS Score v2.0
    def calculate_aps_score(row):
        equity_pct = row['Equity %']
        loan_age = row['Loan_Age_Mo']
        ltv_pct = row['LTV %']
        
        # Equity component (0-100)
        equity_score = equity_pct
        
        # Loan age component (optimal 18-36 months)
        if loan_age < 18:
            age_score = (loan_age / 18) * 50
        elif loan_age <= 36:
            age_score = 100
        elif loan_age <= 60:
            age_score = 100 - ((loan_age - 36) / 24) * 30
        else:
            age_score = max(40, 70 - ((loan_age - 60) / 60) * 30)
        
        # LTV component (lower is better)
        ltv_score = 100 - ltv_pct
        
        # Weighted combination
        aps_score = (equity_score * 0.40 + age_score * 0.30 + ltv_score * 0.30)
        return round(aps_score, 1)
    
    df['APS_Score (v2.0)'] = df.apply(calculate_aps_score, axis=1)
    
    # Assign APS Tier
    def assign_tier(row):
        score = row['APS_Score (v2.0)']
        ltv = row['LTV %']
        equity_dollars = row['Equity_Dollars']
        
        if score >= 80 and ltv <= 30 and equity_dollars >= 500000:
            return 'Platinum'
        elif score >= 65 and ltv <= 50 and equity_dollars >= 300000:
            return 'Gold'
        elif score >= 50 and ltv <= 65 and equity_dollars >= 200000:
            return 'Silver'
        else:
            return 'Nurture'
    
    df['APS_Tier'] = df.apply(assign_tier, axis=1)
    
    # Calculate CCI (Credit Confidence Index)
    def calculate_cci(row):
        equity_pct = row['Equity %']
        ltv_pct = row['LTV %']
        loan_age = row['Loan_Age_Mo']
        
        # Equity component (0-40 points)
        equity_component = min(40, (equity_pct / 100) * 40)
        
        # LTV component (0-35 points)
        ltv_component = max(0, 35 - (ltv_pct / 100) * 35)
        
        # Loan age component (0-25 points)
        if loan_age >= 18:
            age_component = min(25, 25 * (loan_age / 60))
        else:
            age_component = (loan_age / 18) * 15
        
        cci = equity_component + ltv_component + age_component
        return round(cci, 1)
    
    df['CCI'] = df.apply(calculate_cci, axis=1)
    
    # Clean up temporary columns
    df = df.drop(columns=['_property_value', '_loan_balance', '_loan_date'], errors='ignore')
    
    return df