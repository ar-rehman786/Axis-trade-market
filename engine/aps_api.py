# # aps_api.py - APS Market Intelligence API (FastAPI)
# """
# Backend API matching client's TypeScript server.ts
# Endpoints:
# - GET /v1/pulse - Quick market health check
# - GET /v1/market-intel - City/ZIP market intelligence
# """

# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional, Dict, Any
# from datetime import datetime
# from pathlib import Path
# import json

# import engine.aps_metrics as metrics
# from engine.aps_database import MarketDataDB

# # Initialize FastAPI app
# app = FastAPI(
#     title="APS Market Intelligence API",
#     description="Real-time market intelligence for equity analysis and churn prediction",
#     version="1.0.0"
# )

# # CORS middleware (allow all origins for development)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize database
# db = MarketDataDB()

# # ==================== SAMPLE DATA (Fallback) ====================

# SAMPLE_DATA = {
#     "byZip": {
#         "27609": {
#             "zip": "27609",
#             "city": "Raleigh",
#             "state": "NC",
#             "updated_at": "2024-10-01",
#             "metrics": {
#                 "tip_zip_score": 88,
#                 "median_dom": 19,
#                 "equity_delta_90d": 3.4,
#                 "refi_pressure": 78
#             }
#         },
#         "27613": {
#             "zip": "27613",
#             "city": "Raleigh",
#             "state": "NC",
#             "updated_at": "2024-10-01",
#             "metrics": {
#                 "tip_zip_score": 91,
#                 "median_dom": 21,
#                 "equity_delta_90d": 2.9,
#                 "refi_pressure": 72
#             }
#         }
#     },
#     "byCity": {
#         "Raleigh": {
#             "city": "Raleigh",
#             "state": "NC",
#             "updated_at": "2024-10-01",
#             "summary": {
#                 "median_ltv": 0.53,
#                 "median_equity_pct": 0.47,
#                 "median_equity_dollars": 184000,
#                 "median_loan_age_months": 52,
#                 "refi_pressure": 74,
#                 "equity_delta_90d": 3.1
#             },
#             "zips": [
#                 {
#                     "zip": "27609",
#                     "tip_zip_score": 93,
#                     "median_dom": 19,
#                     "equity_delta_90d": 3.4,
#                     "refi_pressure": 78
#                 },
#                 {
#                     "zip": "27613",
#                     "tip_zip_score": 91,
#                     "median_dom": 21,
#                     "equity_delta_90d": 2.9,
#                     "refi_pressure": 72
#                 }
#             ]
#         }
#     }
# }

# # ==================== ENDPOINTS ====================

# @app.get("/")
# def root():
#     """API health check"""
#     return {
#         "status": "online",
#         "service": "APS Market Intelligence API",
#         "version": "1.0.0",
#         "timestamp": datetime.now().isoformat()
#     }

# @app.get("/v1/pulse")
# def get_pulse():
#     """
#     Quick market health snapshot
    
#     Returns:
#         equity: Median equity delta (90 days)
#         refi: Refinance pressure index (0-100)
#         count: Number of active markets
    
#     Example:
#         GET /v1/pulse
#         Response: {"equity": 3.9, "refi": 74, "count": 50}
#     """
#     try:
#         # Try to get from database
#         pulse_data = db.get_pulse_data()
        
#         if pulse_data:
#             return pulse_data
#         else:
#             # Fallback to sample data
#             return {
#                 "equity": 3.9,
#                 "refi": 74,
#                 "count": 50
#             }
#     except Exception as e:
#         print(f"⚠ Pulse endpoint error: {e}")
#         return {
#             "equity": 3.9,
#             "refi": 74,
#             "count": 50
#         }

# @app.get("/v1/market-intel")
# def get_market_intel(
#     city: Optional[str] = Query(None, description="City name (e.g., 'Raleigh')"),
#     zip_code: Optional[str] = Query(None, alias="zip", description="ZIP code (e.g., '27609')")
# ):
#     """
#     Get detailed market intelligence by city or ZIP
    
#     Args:
#         city: City name (optional)
#         zip_code: ZIP code (optional)
    
#     Returns:
#         ZIP data: { zip, city, state, updated_at, metrics }
#         City data: { city, state, updated_at, summary, zips[] }
    
#     Examples:
#         GET /v1/market-intel?zip=27609
#         GET /v1/market-intel?city=Raleigh
#     """
    
#     # Validate input
#     if not city and not zip_code:
#         raise HTTPException(
#             status_code=400,
#             detail="Either 'city' or 'zip' parameter required"
#         )
    
#     try:
#         # Try database first
#         if zip_code:
#             data = db.get_zip_data(zip_code)
#             if not data:
#                 # Fallback to sample data
#                 data = SAMPLE_DATA["byZip"].get(zip_code)
#         else:
#             data = db.get_city_data(city)
#             if not data:
#                 # Fallback to sample data
#                 data = SAMPLE_DATA["byCity"].get(city)
        
#         if not data:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"No data found for {'ZIP ' + zip_code if zip_code else 'city ' + city}"
#             )
        
#         return data
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"⚠ Market intel error: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Internal server error: {str(e)}"
#         )

# @app.post("/v1/calculate")
# def calculate_metrics(
#     loan: float = Query(..., description="Total loan balance"),
#     value: float = Query(..., description="Property value"),
#     loan_date: Optional[str] = Query(None, description="Last loan date (ISO format)"),
#     equity_delta: float = Query(0, description="Equity change over 90 days")
# ):
#     """
#     Calculate APS metrics for a single property
    
#     Args:
#         loan: Total loan balance
#         value: Property value
#         loan_date: Last loan date (ISO format, optional)
#         equity_delta: Equity delta over 90 days
    
#     Returns:
#         Calculated metrics: ltv, equity_pct, aps_score, churn_index, etc.
    
#     Example:
#         POST /v1/calculate?loan=200000&value=400000&equity_delta=5000
#     """
    
#     today = datetime.now().isoformat()[:10]
    
#     # Calculate metrics
#     ltv_val = metrics.ltv(loan, value)
#     equity_pct_val = metrics.equity_pct(ltv_val)
#     equity_dollars_val = metrics.equity_dollars(value, loan)
    
#     loan_age = 0
#     if loan_date:
#         loan_age = metrics.loan_age_months(today, loan_date)
    
#     aps_score_val = metrics.aps_score(ltv_val, equity_pct_val, loan_age, equity_delta)
    
#     # Estimate cycle phase and velocity
#     if loan_age < 18:
#         cycle_phase = loan_age / 18 * 0.5
#     elif loan_age <= 36:
#         cycle_phase = 0.5 + (loan_age - 18) / 18 * 0.5
#     else:
#         cycle_phase = max(0.3, 1.0 - (loan_age - 36) / 60 * 0.7)
    
#     velocity = metrics.clip((equity_delta + 5) / 10, 0, 1)
#     churn_val = metrics.churn_index(cycle_phase, velocity)
    
#     return {
#         "ltv": round(ltv_val * 100, 2),  # Return as percentage
#         "equity_pct": round(equity_pct_val * 100, 2),
#         "equity_dollars": round(equity_dollars_val, 2),
#         "loan_age_months": loan_age,
#         "aps_score": round(aps_score_val, 1),
#         "churn_index": round(churn_val, 1),
#         "cycle_phase": round(cycle_phase, 2),
#         "velocity": round(velocity, 2)
#     }

# @app.get("/v1/health")
# def health_check():
#     """
#     Detailed API health check
    
#     Returns:
#         status, database_connected, uptime, etc.
#     """
#     return {
#         "status": "healthy",
#         "database_connected": db.is_connected(),
#         "endpoints": [
#             "/v1/pulse",
#             "/v1/market-intel",
#             "/v1/calculate",
#             "/v1/health"
#         ],
#         "timestamp": datetime.now().isoformat()
#     }

# # ==================== STARTUP/SHUTDOWN ====================

# @app.on_event("startup")
# def startup_event():
#     """Initialize database on startup"""
#     print("=" * 60)
#     print("APS Market Intelligence API - Starting")
#     print("=" * 60)
#     db.initialize()
#     print("✓ Database initialized")
#     print("✓ API ready at http://localhost:8080")
#     print("✓ Docs available at http://localhost:8080/docs")
#     print("=" * 60)

# @app.on_event("shutdown")
# def shutdown_event():
#     """Clean up on shutdown"""
#     print("\n" + "=" * 60)
#     print("APS Market Intelligence API - Shutting down")
#     print("=" * 60)
#     db.close()
#     print("✓ Database closed")

# # ==================== RUN SERVER ====================

# if __name__ == "__main__":
#     import uvicorn
    
#     print("\nStarting APS Market Intelligence API...")
#     print("Press Ctrl+C to stop\n")
    
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8080,
#         log_level="info"
#     )


# aps_api.py - APS Market Intelligence API (Production-Ready)
"""
Production REST API with job tracking, chunked processing, and feed routing
Client Requirements: Phase 1 Implementation
"""

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, HttpUrl
import uuid
import pandas as pd
import json
import requests
from enum import Enum

import engine.aps_metrics as metrics
from engine.aps_database import MarketDataDB
from engine.aps_feed_config import detect_feed_type, get_feed_config
from engine.aps_normalize import normalize_and_score
from engine.aps_render import render_pdf

# ==================== MODELS ====================

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class IngestRequest(BaseModel):
    market: str
    file_url: HttpUrl
    schema_version: str = "v2.0"
    alias_map: Optional[Dict[str, List[str]]] = None
    chunk_rows: int = 2000

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    counts: Optional[Dict[str, int]] = None
    error: Optional[str] = None

# ==================== APP SETUP ====================

app = FastAPI(
    title="APS Market Intelligence API",
    description="Production API for market intelligence data processing with feed routing",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = MarketDataDB()

# Job storage (In production: use Redis/PostgreSQL)
JOBS = {}

# Output directory
OUTPUT_DIR = Path("APS_Market_Intelligence_Live")
OUTPUT_DIR.mkdir(exist_ok=True)

# ==================== ALIAS MAPPING ====================

DEFAULT_ALIAS_MAP = {
    "property_address": ["Address", "Property Address", "Street Address", "Property_Address"],
    "city": ["City", "City Name", "Municipality"],
    "state": ["State", "ST", "State Code"],
    "zip": ["ZIP", "Zip Code", "Postal Code", "ZipCode"],
    "owner_name": ["Owner Name", "Owner", "Owner OO", "OwnerName"],
    "loan_date": ["LastLoanDate", "Loan Date", "Last Loan Date", "Loan 1 Date"],
    "loan_balance": ["TotalLoanBal", "Loan Balance", "Total Loan Balance"],
    "property_value": ["EstValue", "Property Value", "Est Value", "AVM"],
    "ltv": ["LTV %", "LTV", "Loan to Value"],
    "equity": ["Equity %", "Equity Pct", "Equity Percentage"]
}

# ==================== DNC/CONSENT FILTERING ====================

def apply_dnc_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out Do Not Contact records"""
    original_count = len(df)
    
    # Remove records with DNC flag
    if 'dnc_flag' in df.columns:
        df = df[df['dnc_flag'] != True]
    
    # Remove records without consent
    if 'consent' in df.columns:
        df = df[df['consent'] != False]
    
    filtered_count = original_count - len(df)
    if filtered_count > 0:
        print(f"  ⚠ Filtered {filtered_count} records due to DNC/consent")
    
    return df

# ==================== SCHEMA VALIDATION ====================

REQUIRED_FIELDS_V2 = ["property_address", "city", "state", "zip"]

def validate_schema(df: pd.DataFrame, schema_version: str = "v2.0") -> tuple[bool, str]:
    """Validate DataFrame against schema"""
    
    if schema_version == "v2.0":
        required = REQUIRED_FIELDS_V2
    else:
        return False, f"Unknown schema version: {schema_version}"
    
    # Check for required columns
    df_cols = [col.lower().replace(' ', '_') for col in df.columns]
    missing = [field for field in required if field not in df_cols]
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, "Schema valid"

# ==================== COLUMN ALIAS MAPPING ====================

def apply_alias_mapping(df: pd.DataFrame, alias_map: Dict[str, List[str]] = None) -> pd.DataFrame:
    """Map column names using alias map"""
    
    if alias_map is None:
        alias_map = DEFAULT_ALIAS_MAP
    
    # Create reverse mapping: alias -> standard_name
    reverse_map = {}
    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            reverse_map[alias] = standard_name
    
    # Rename columns
    rename_dict = {}
    for col in df.columns:
        if col in reverse_map:
            rename_dict[col] = reverse_map[col]
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
        print(f"  ✓ Mapped {len(rename_dict)} column aliases")
    
    return df

# ==================== CHUNKED PROCESSING ====================

def process_file_in_chunks(file_path: Path, chunk_rows: int, job_id: str) -> Dict[str, Any]:
    """Process large CSV file in chunks"""
    
    results = {
        "total_rows": 0,
        "processed_rows": 0,
        "failed_rows": 0,
        "feeds": {}
    }
    
    try:
        # Read CSV in chunks
        chunk_iterator = pd.read_csv(file_path, chunksize=chunk_rows, encoding='utf-8-sig')
        
        for i, chunk in enumerate(chunk_iterator):
            print(f"  → Processing chunk {i+1} ({len(chunk)} rows)...")
            
            results["total_rows"] += len(chunk)
            
            # Apply alias mapping
            chunk = apply_alias_mapping(chunk)
            
            # Apply DNC filter
            chunk = apply_dnc_filter(chunk)
            
            # Normalize and score
            chunk = normalize_and_score(chunk)
            
            # Detect feed type
            feed_type = detect_feed_type(data=chunk)
            
            # Track feed counts
            if feed_type not in results["feeds"]:
                results["feeds"][feed_type] = 0
            results["feeds"][feed_type] += len(chunk)
            
            results["processed_rows"] += len(chunk)
            
            # Update job progress
            JOBS[job_id]["counts"] = results
            JOBS[job_id]["progress"] = (results["processed_rows"] / results["total_rows"]) * 100
        
        return results
        
    except Exception as e:
        print(f"  ✗ Chunk processing error: {e}")
        results["failed_rows"] = results["total_rows"] - results["processed_rows"]
        raise

# ==================== BACKGROUND JOB PROCESSING ====================

async def process_job(job_id: str, file_url: str, market: str, schema_version: str, 
                     alias_map: Dict, chunk_rows: int):
    """Background task to process ingestion job"""
    
    try:
        JOBS[job_id]["status"] = JobStatus.PROCESSING
        print(f"\n{'='*60}")
        print(f"Processing Job: {job_id}")
        print(f"{'='*60}")
        
        # Download file
        print(f"  → Downloading file from {file_url}...")
        response = requests.get(str(file_url), timeout=60)
        response.raise_for_status()
        
        # Save temporarily
        temp_file = OUTPUT_DIR / f"{job_id}_input.csv"
        temp_file.write_bytes(response.content)
        print(f"  ✓ Downloaded {len(response.content)} bytes")
        
        # Validate schema
        df_sample = pd.read_csv(temp_file, nrows=5)
        valid, message = validate_schema(df_sample, schema_version)
        if not valid:
            raise ValueError(message)
        print(f"  ✓ Schema validation passed")
        
        # Process in chunks
        print(f"  → Processing file (chunk_rows={chunk_rows})...")
        results = process_file_in_chunks(temp_file, chunk_rows, job_id)
        
        # Load full processed data
        df = pd.read_csv(temp_file, encoding='utf-8-sig')
        df = apply_alias_mapping(df, alias_map)
        df = apply_dnc_filter(df)
        df = normalize_and_score(df)
        
        # Generate outputs per feed
        print(f"  → Generating outputs per feed...")
        feed_outputs = {}
        
        for feed_type, count in results["feeds"].items():
            feed_df = df[df.apply(lambda row: detect_feed_type(data=pd.DataFrame([row])) == feed_type, axis=1)]
            
            # Save feed CSV
            feed_csv = OUTPUT_DIR / f"{job_id}_{feed_type}_output.csv"
            feed_df.to_csv(feed_csv, index=False, encoding='utf-8-sig')
            
            # Generate PDF
            feed_pdf = OUTPUT_DIR / f"{job_id}_{feed_type}_report.pdf"
            render_pdf(feed_df, feed_pdf, market_name=market, quarter=4, year=2025)
            
            feed_outputs[feed_type] = {
                "csv": str(feed_csv),
                "pdf": str(feed_pdf),
                "count": count
            }
            
            print(f"    ✓ {feed_type}: {count} rows → CSV + PDF")
        
        # Update job status
        JOBS[job_id]["status"] = JobStatus.COMPLETED
        JOBS[job_id]["counts"] = results
        JOBS[job_id]["outputs"] = feed_outputs
        JOBS[job_id]["completed_at"] = datetime.now().isoformat()
        
        # Clean up temp file
        temp_file.unlink()
        
        print(f"{'='*60}")
        print(f"Job {job_id} completed successfully")
        print(f"{'='*60}\n")
        
    except Exception as e:
        JOBS[job_id]["status"] = JobStatus.FAILED
        JOBS[job_id]["error"] = str(e)
        print(f"  ✗ Job {job_id} failed: {e}")

# ==================== API ENDPOINTS ====================

@app.get("/health")
def health_check():
    """
    Health check endpoint (Client requirement)
    
    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}

@app.post("/ingest")
async def ingest_file(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest CSV file for processing
    
    Client Requirements:
    - Accept file_url for 1k+ rows
    - Process in chunks (chunk_rows parameter)
    - Apply alias_map, schema validation, DNC/consent gating
    - Route to appropriate feeds
    - Generate per-feed CSVs and 7-page PDFs
    
    Args:
        request: IngestRequest model
        
    Returns:
        {"job_id": "uuid"}
    """
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    JOBS[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "market": request.market,
        "file_url": str(request.file_url),
        "schema_version": request.schema_version,
        "chunk_rows": request.chunk_rows,
        "created_at": datetime.now().isoformat(),
        "counts": None,
        "outputs": None,
        "error": None,
        "progress": 0
    }
    
    # Start background processing
    background_tasks.add_task(
        process_job,
        job_id,
        str(request.file_url),
        request.market,
        request.schema_version,
        request.alias_map or DEFAULT_ALIAS_MAP,
        request.chunk_rows
    )
    
    return {"job_id": job_id}

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    """
    Get job status and counts
    
    Returns:
        {
            "job_id": "...",
            "status": "processing|completed|failed",
            "counts": {
                "total_rows": 5000,
                "processed": 5000,
                "failed": 0
            }
        }
    """
    
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = JOBS[job_id]
    
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "market": job["market"],
        "created_at": job["created_at"],
        "completed_at": job.get("completed_at"),
        "progress": job.get("progress", 0),
        "counts": job.get("counts"),
        "error": job.get("error")
    }

@app.get("/feeds")
def get_feed_breakdown(job_id: str = Query(..., description="Job ID")):
    """
    Get feed breakdown for a job
    
    Returns:
        {
            "feeds": [
                {"feed": "core_equity", "count": 1200},
                {"feed": "predictive_churn", "count": 800}
            ]
        }
    """
    
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = JOBS[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job {job_id} not completed yet")
    
    counts = job.get("counts", {}).get("feeds", {})
    
    feeds = [{"feed": feed, "count": count} for feed, count in counts.items()]
    
    return {"feeds": feeds}

@app.get("/report")
def get_report(
    job_id: str = Query(..., description="Job ID"),
    feed: str = Query(..., description="Feed type (e.g., 'core_equity')"),
    format: str = Query("pdf", description="Output format (pdf only for now)")
):
    """
    Download report for a specific feed
    
    Returns:
        PDF file or signed URL (for production with cloud storage)
    """
    
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = JOBS[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job {job_id} not completed yet")
    
    outputs = job.get("outputs", {})
    
    if feed not in outputs:
        raise HTTPException(status_code=404, detail=f"Feed {feed} not found for job {job_id}")
    
    if format == "pdf":
        pdf_path = Path(outputs[feed]["pdf"])
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{job_id}_{feed}_report.pdf"
        )
    else:
        raise HTTPException(status_code=400, detail="Only PDF format supported")

# ==================== LEGACY ENDPOINTS (Backward Compatibility) ====================

@app.get("/v1/pulse")
def get_pulse():
    """Legacy: Quick market health snapshot"""
    try:
        pulse_data = db.get_pulse_data()
        return pulse_data if pulse_data else {"equity": 3.9, "refi": 74, "count": 50}
    except Exception as e:
        return {"equity": 3.9, "refi": 74, "count": 50}

@app.get("/v1/market-intel")
def get_market_intel(
    city: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None, alias="zip")
):
    """Legacy: Get market intelligence by city or ZIP"""
    if not city and not zip_code:
        raise HTTPException(status_code=400, detail="Either 'city' or 'zip' required")
    
    try:
        if zip_code:
            data = db.get_zip_data(zip_code)
        else:
            data = db.get_city_data(city)
        
        if not data:
            raise HTTPException(status_code=404, detail="Data not found")
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
def startup_event():
    """Initialize on startup"""
    print("=" * 60)
    print("APS Market Intelligence API v2.0 - Starting")
    print("=" * 60)
    db.initialize()
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("✓ Database initialized")
    print("✓ Output directory created")
    print("✓ API ready at http://localhost:8080")
    print("✓ Docs at http://localhost:8080/docs")
    print("=" * 60)

@app.on_event("shutdown")
def shutdown_event():
    """Clean up on shutdown"""
    db.close()
    print("✓ API shut down gracefully")

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")