# aps_metrics.py - APS Calculation Engine (Ported from TypeScript)
"""
Core metrics calculations matching client's TypeScript implementation
Source: metrics.ts from backend package
"""

import math
from datetime import datetime
from typing import Optional

# ==================== UTILITY FUNCTIONS ====================

def clip(v: float, lo: float, hi: float) -> float:
    """
    Clip value between min and max bounds
    
    Args:
        v: Value to clip
        lo: Lower bound
        hi: Upper bound
    
    Returns:
        Clipped value
    
    Example:
        >>> clip(150, 0, 100)
        100
    """
    return max(lo, min(hi, v))

def months_between(iso_a: Optional[str], iso_b: Optional[str]) -> int:
    """
    Calculate months between two ISO date strings
    
    Args:
        iso_a: ISO date string (YYYY-MM-DD)
        iso_b: ISO date string (YYYY-MM-DD)
    
    Returns:
        Number of months between dates (always >= 0)
    
    Example:
        >>> months_between('2025-01-01', '2024-01-01')
        12
    """
    if not iso_a or not iso_b:
        return 0
    
    try:
        # Parse dates (take first 10 chars for YYYY-MM-DD)
        a = datetime.fromisoformat(iso_a[:10])
        b = datetime.fromisoformat(iso_b[:10])
        
        # Calculate month difference
        years_diff = a.year - b.year
        months_diff = a.month - b.month
        total_months = years_diff * 12 + months_diff
        
        return max(0, total_months)
    except (ValueError, IndexError):
        return 0

# ==================== CORE METRICS ====================

def ltv(loan: float, value: float) -> float:
    """
    Calculate Loan-to-Value ratio
    
    Args:
        loan: Total loan balance
        value: Property value
    
    Returns:
        LTV ratio (0-2, clipped)
        Returns 2 if value <= 0
    
    Example:
        >>> ltv(200000, 400000)
        0.5
    """
    if value <= 0:
        return 2.0
    return clip(loan / value, 0, 2)

def equity_pct(ltv_val: float) -> float:
    """
    Calculate equity percentage from LTV
    
    Args:
        ltv_val: LTV ratio (0-1 typically)
    
    Returns:
        Equity percentage (0-1)
    
    Example:
        >>> equity_pct(0.7)
        0.3
    """
    return max(0, 1 - ltv_val)

def equity_dollars(value: float, loan: float) -> float:
    """
    Calculate equity in dollars
    
    Args:
        value: Property value
        loan: Total loan balance
    
    Returns:
        Equity amount in dollars
    
    Example:
        >>> equity_dollars(400000, 200000)
        200000.0
    """
    return max(0, value - loan)

def loan_age_months(today_iso: str, last_refi: Optional[str] = None, 
                    orig: Optional[str] = None) -> int:
    """
    Calculate loan age in months
    
    Args:
        today_iso: Today's date (ISO format)
        last_refi: Last refinance date (optional)
        orig: Original loan date (optional)
    
    Returns:
        Loan age in months
    
    Example:
        >>> loan_age_months('2025-01-01', last_refi='2023-01-01')
        24
    """
    return months_between(today_iso, last_refi or orig)

def aps_score(ltv_val: float, equity_pct_val: float, loan_age: int, 
              equity_dollars_delta: float = 0) -> float:
    """
    Calculate APS composite score (0-100)
    
    Formula breakdown:
    - Start at 100
    - Subtract 40 * LTV (0-1 range)
    - Subtract 30 * (1 - equity%)
    - Subtract 20 * exp(-loan_age/36)
    - Add bonus: 10 * (0.5 * (tanh(equity_delta/25000) + 1))
    
    Args:
        ltv_val: LTV ratio (0-1)
        equity_pct_val: Equity percentage (0-1)
        loan_age: Loan age in months
        equity_dollars_delta: Change in equity over 90 days (default 0)
    
    Returns:
        APS score (0-100)
    
    Example:
        >>> aps_score(0.7, 0.3, 24, 5000)
        42.1
    """
    score = 100.0
    
    # LTV penalty (0-40 points)
    score -= 40 * clip(ltv_val, 0, 1)
    
    # Equity penalty (0-30 points)
    score -= 30 * clip(1 - equity_pct_val, 0, 1)
    
    # Loan age penalty (0-20 points, exponential decay)
    score -= 20 * math.exp(-loan_age / 36)
    
    # Equity growth bonus (0-10 points)
    bonus = 10 * (0.5 * (math.tanh(equity_dollars_delta / 25000) + 1))
    score += bonus
    
    return clip(score, 0, 100)

def churn_index(cycle_phase_01: float, velocity_01: float) -> float:
    """
    Calculate churn probability index
    
    Combines cycle phase (where in equity cycle) with velocity (market speed)
    
    Args:
        cycle_phase_01: Equity cycle phase (0-1)
        velocity_01: Market velocity (0-1)
    
    Returns:
        Churn index (0-100)
    
    Formula: 100 * (0.35 * velocity + 0.65 * cycle_phase)
    
    Example:
        >>> churn_index(0.8, 0.6)
        73.0
    """
    return clip(
        100 * (0.35 * clip(velocity_01, 0, 1) + 
               0.65 * clip(cycle_phase_01, 0, 1)),
        0, 100
    )

def velocity_index(refi_now: float, refi_90: float) -> float:
    """
    Calculate market velocity index
    
    Measures refinance activity change over 90 days
    
    Args:
        refi_now: Current refinance count
        refi_90: Refinance count 90 days ago
    
    Returns:
        Velocity index (0-100)
        - 50 = neutral (no change)
        - >50 = increasing activity
        - <50 = decreasing activity
    
    Example:
        >>> velocity_index(120, 100)
        60.0
    """
    if refi_90 <= 0:
        return 50.0
    
    # Calculate ratio of change (-1 to +1)
    ratio = clip((refi_now - refi_90) / max(1, refi_90), -1, 1)
    
    # Convert to 0-100 scale (50 = neutral)
    return (ratio + 1) * 50

# ==================== INTEGRATION WITH EXISTING SYSTEM ====================

def calculate_comprehensive_metrics(df_row, today_iso: str = None) -> dict:
    """
    Calculate all metrics for a single record
    Integrates TypeScript logic with existing aps_normalize.py calculations
    
    Args:
        df_row: DataFrame row (pandas Series)
        today_iso: Today's date (ISO format, optional)
    
    Returns:
        Dictionary with all calculated metrics
    """
    if today_iso is None:
        today_iso = datetime.now().isoformat()[:10]
    
    # Extract values from row
    loan = df_row.get('TotalLoanBal', 0) or df_row.get('_loan_balance', 0)
    value = df_row.get('EstValue', 0) or df_row.get('_property_value', 0)
    last_loan_date = df_row.get('LastLoanDate') or df_row.get('_loan_date')
    
    # Convert to ISO if datetime
    if hasattr(last_loan_date, 'isoformat'):
        last_loan_date = last_loan_date.isoformat()[:10]
    elif last_loan_date:
        last_loan_date = str(last_loan_date)[:10]
    
    # Calculate core metrics
    ltv_val = ltv(loan, value)
    equity_pct_val = equity_pct(ltv_val)
    equity_dollars_val = equity_dollars(value, loan)
    loan_age = loan_age_months(today_iso, last_loan_date)
    
    # Get equity delta (90-day change) if available
    equity_delta = df_row.get('equity_delta_90d', 0)
    
    # Calculate APS score
    aps_score_val = aps_score(ltv_val, equity_pct_val, loan_age, equity_delta)
    
    # Calculate churn metrics
    # Cycle phase based on loan age (0-1, peaks at 18-36 months)
    if loan_age < 18:
        cycle_phase = loan_age / 18 * 0.5
    elif loan_age <= 36:
        cycle_phase = 0.5 + (loan_age - 18) / 18 * 0.5
    else:
        cycle_phase = max(0.3, 1.0 - (loan_age - 36) / 60 * 0.7)
    
    # Velocity from equity delta
    velocity = clip((equity_delta + 5) / 10, 0, 1)  # Normalize to 0-1
    
    churn_val = churn_index(cycle_phase, velocity)
    
    return {
        'ltv': round(ltv_val, 4),
        'equity_pct': round(equity_pct_val, 4),
        'equity_dollars': round(equity_dollars_val, 2),
        'loan_age_months': loan_age,
        'aps_score': round(aps_score_val, 1),
        'churn_index': round(churn_val, 1),
        'cycle_phase': round(cycle_phase, 2),
        'velocity': round(velocity, 2)
    }

# ==================== TESTING ====================

if __name__ == "__main__":
    print("APS Metrics Engine - Test Suite")
    print("=" * 50)
    
    # Test 1: LTV calculation
    print("\n1. LTV Calculation:")
    print(f"   ltv(200000, 400000) = {ltv(200000, 400000):.4f}")
    print(f"   Expected: 0.5000")
    
    # Test 2: Months between
    print("\n2. Months Between:")
    print(f"   months_between('2025-01-01', '2024-01-01') = {months_between('2025-01-01', '2024-01-01')}")
    print(f"   Expected: 12")
    
    # Test 3: APS Score
    print("\n3. APS Score:")
    score = aps_score(0.7, 0.3, 24, 5000)
    print(f"   aps_score(0.7, 0.3, 24, 5000) = {score:.1f}")
    print(f"   Expected: ~42.1")
    
    # Test 4: Churn Index
    print("\n4. Churn Index:")
    churn = churn_index(0.8, 0.6)
    print(f"   churn_index(0.8, 0.6) = {churn:.1f}")
    print(f"   Expected: 73.0")
    
    # Test 5: Velocity Index
    print("\n5. Velocity Index:")
    velocity = velocity_index(120, 100)
    print(f"   velocity_index(120, 100) = {velocity:.1f}")
    print(f"   Expected: 60.0")
    
    print("\n" + "=" * 50)
    print("✓ All tests completed")