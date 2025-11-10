# aps_api.py - APS Market Intelligence API (FastAPI)
"""
Backend API matching client's TypeScript server.ts
Endpoints:
- GET /v1/pulse - Quick market health check
- GET /v1/market-intel - City/ZIP market intelligence
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json

import engine.aps_metrics as metrics
from engine.aps_database import MarketDataDB

# Initialize FastAPI app
app = FastAPI(
    title="APS Market Intelligence API",
    description="Real-time market intelligence for equity analysis and churn prediction",
    version="1.0.0"
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = MarketDataDB()

# ==================== SAMPLE DATA (Fallback) ====================

SAMPLE_DATA = {
    "byZip": {
        "27609": {
            "zip": "27609",
            "city": "Raleigh",
            "state": "NC",
            "updated_at": "2024-10-01",
            "metrics": {
                "tip_zip_score": 88,
                "median_dom": 19,
                "equity_delta_90d": 3.4,
                "refi_pressure": 78
            }
        },
        "27613": {
            "zip": "27613",
            "city": "Raleigh",
            "state": "NC",
            "updated_at": "2024-10-01",
            "metrics": {
                "tip_zip_score": 91,
                "median_dom": 21,
                "equity_delta_90d": 2.9,
                "refi_pressure": 72
            }
        }
    },
    "byCity": {
        "Raleigh": {
            "city": "Raleigh",
            "state": "NC",
            "updated_at": "2024-10-01",
            "summary": {
                "median_ltv": 0.53,
                "median_equity_pct": 0.47,
                "median_equity_dollars": 184000,
                "median_loan_age_months": 52,
                "refi_pressure": 74,
                "equity_delta_90d": 3.1
            },
            "zips": [
                {
                    "zip": "27609",
                    "tip_zip_score": 93,
                    "median_dom": 19,
                    "equity_delta_90d": 3.4,
                    "refi_pressure": 78
                },
                {
                    "zip": "27613",
                    "tip_zip_score": 91,
                    "median_dom": 21,
                    "equity_delta_90d": 2.9,
                    "refi_pressure": 72
                }
            ]
        }
    }
}

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """API health check"""
    return {
        "status": "online",
        "service": "APS Market Intelligence API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/v1/pulse")
def get_pulse():
    """
    Quick market health snapshot
    
    Returns:
        equity: Median equity delta (90 days)
        refi: Refinance pressure index (0-100)
        count: Number of active markets
    
    Example:
        GET /v1/pulse
        Response: {"equity": 3.9, "refi": 74, "count": 50}
    """
    try:
        # Try to get from database
        pulse_data = db.get_pulse_data()
        
        if pulse_data:
            return pulse_data
        else:
            # Fallback to sample data
            return {
                "equity": 3.9,
                "refi": 74,
                "count": 50
            }
    except Exception as e:
        print(f"⚠ Pulse endpoint error: {e}")
        return {
            "equity": 3.9,
            "refi": 74,
            "count": 50
        }

@app.get("/v1/market-intel")
def get_market_intel(
    city: Optional[str] = Query(None, description="City name (e.g., 'Raleigh')"),
    zip_code: Optional[str] = Query(None, alias="zip", description="ZIP code (e.g., '27609')")
):
    """
    Get detailed market intelligence by city or ZIP
    
    Args:
        city: City name (optional)
        zip_code: ZIP code (optional)
    
    Returns:
        ZIP data: { zip, city, state, updated_at, metrics }
        City data: { city, state, updated_at, summary, zips[] }
    
    Examples:
        GET /v1/market-intel?zip=27609
        GET /v1/market-intel?city=Raleigh
    """
    
    # Validate input
    if not city and not zip_code:
        raise HTTPException(
            status_code=400,
            detail="Either 'city' or 'zip' parameter required"
        )
    
    try:
        # Try database first
        if zip_code:
            data = db.get_zip_data(zip_code)
            if not data:
                # Fallback to sample data
                data = SAMPLE_DATA["byZip"].get(zip_code)
        else:
            data = db.get_city_data(city)
            if not data:
                # Fallback to sample data
                data = SAMPLE_DATA["byCity"].get(city)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {'ZIP ' + zip_code if zip_code else 'city ' + city}"
            )
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠ Market intel error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/v1/calculate")
def calculate_metrics(
    loan: float = Query(..., description="Total loan balance"),
    value: float = Query(..., description="Property value"),
    loan_date: Optional[str] = Query(None, description="Last loan date (ISO format)"),
    equity_delta: float = Query(0, description="Equity change over 90 days")
):
    """
    Calculate APS metrics for a single property
    
    Args:
        loan: Total loan balance
        value: Property value
        loan_date: Last loan date (ISO format, optional)
        equity_delta: Equity delta over 90 days
    
    Returns:
        Calculated metrics: ltv, equity_pct, aps_score, churn_index, etc.
    
    Example:
        POST /v1/calculate?loan=200000&value=400000&equity_delta=5000
    """
    
    today = datetime.now().isoformat()[:10]
    
    # Calculate metrics
    ltv_val = metrics.ltv(loan, value)
    equity_pct_val = metrics.equity_pct(ltv_val)
    equity_dollars_val = metrics.equity_dollars(value, loan)
    
    loan_age = 0
    if loan_date:
        loan_age = metrics.loan_age_months(today, loan_date)
    
    aps_score_val = metrics.aps_score(ltv_val, equity_pct_val, loan_age, equity_delta)
    
    # Estimate cycle phase and velocity
    if loan_age < 18:
        cycle_phase = loan_age / 18 * 0.5
    elif loan_age <= 36:
        cycle_phase = 0.5 + (loan_age - 18) / 18 * 0.5
    else:
        cycle_phase = max(0.3, 1.0 - (loan_age - 36) / 60 * 0.7)
    
    velocity = metrics.clip((equity_delta + 5) / 10, 0, 1)
    churn_val = metrics.churn_index(cycle_phase, velocity)
    
    return {
        "ltv": round(ltv_val * 100, 2),  # Return as percentage
        "equity_pct": round(equity_pct_val * 100, 2),
        "equity_dollars": round(equity_dollars_val, 2),
        "loan_age_months": loan_age,
        "aps_score": round(aps_score_val, 1),
        "churn_index": round(churn_val, 1),
        "cycle_phase": round(cycle_phase, 2),
        "velocity": round(velocity, 2)
    }

@app.get("/v1/health")
def health_check():
    """
    Detailed API health check
    
    Returns:
        status, database_connected, uptime, etc.
    """
    return {
        "status": "healthy",
        "database_connected": db.is_connected(),
        "endpoints": [
            "/v1/pulse",
            "/v1/market-intel",
            "/v1/calculate",
            "/v1/health"
        ],
        "timestamp": datetime.now().isoformat()
    }

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    print("=" * 60)
    print("APS Market Intelligence API - Starting")
    print("=" * 60)
    db.initialize()
    print("✓ Database initialized")
    print("✓ API ready at http://localhost:8080")
    print("✓ Docs available at http://localhost:8080/docs")
    print("=" * 60)

@app.on_event("shutdown")
def shutdown_event():
    """Clean up on shutdown"""
    print("\n" + "=" * 60)
    print("APS Market Intelligence API - Shutting down")
    print("=" * 60)
    db.close()
    print("✓ Database closed")

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\nStarting APS Market Intelligence API...")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )