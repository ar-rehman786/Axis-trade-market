# aps_feed_config.py - Feed Type Configuration & Router
"""
APS Market Intelligence - Feed Type Router
Dynamically generates different 7-page layouts based on feed type
"""

# Feed Type Registry
FEED_TYPES = {
    "core_equity": {
        "name": "APS Core Equity Feed",
        "description": "Refi-ready, owner-occupied records (≤80% LTV, 18–36 mo loan age)",
        "pages": [
            "cover_summary",
            "zip_insights",
            "institutional_opportunity",
            "heat_map",
            "churn_triangle",
            "qa_schema",
            "sample_data"
        ],
        "color_theme": "teal",
        "keywords": ["core", "equity", "refi"]
    },
    
    "transactional_momentum": {
        "name": "APS Transactional Momentum Feed",
        "description": "3–12 mo refi/sale velocity + ownership turnover tracking",
        "pages": [
            "cover_summary",
            "transaction_velocity",
            "dom_analysis",
            "market_activity",
            "velocity_curves",
            "qa_schema",
            "sample_data"
        ],
        "color_theme": "yellow",
        "keywords": ["transaction", "momentum", "velocity"]
    },
    
    "predictive_churn": {
        "name": "APS Predictive Churn Feed",
        "description": "Refi/sale prediction (90-day outlook) using equity rate + loan aging",
        "pages": [
            "cover_summary",
            "churn_models",
            "dual_model_framework",
            "risk_tiers",
            "prediction_matrix",
            "qa_schema",
            "sample_data"
        ],
        "color_theme": "red",
        "keywords": ["churn", "predictive", "forecast"]
    },
    
    "market_activity": {
        "name": "APS Market Activity Feed",
        "description": "DOM, listing movement, pricing trends — for brokers/investors",
        "pages": [
            "cover_summary",
            "listing_movement",
            "pricing_trends",
            "dom_heatmap",
            "market_velocity",
            "qa_schema",
            "sample_data"
        ],
        "color_theme": "blue",
        "keywords": ["market", "activity", "dom", "listing"]
    },
    
    "lender_engagement": {
        "name": "APS Lender Engagement Feed",
        "description": "Lender rate patterns, volume mapping, product targeting",
        "pages": [
            "cover_summary",
            "lender_patterns",
            "rate_analysis",
            "volume_mapping",
            "product_targeting",
            "qa_schema",
            "sample_data"
        ],
        "color_theme": "orange",
        "keywords": ["lender", "engagement", "rate", "volume"]
    }
}

# Color themes
COLOR_THEMES = {
    "teal": {"primary": "#00D1D1", "secondary": "#FFD166", "accent": "#FF6B6B"},
    "yellow": {"primary": "#FFD166", "secondary": "#00D1D1", "accent": "#FF6B6B"},
    "red": {"primary": "#FF6B6B", "secondary": "#FFD166", "accent": "#00D1D1"},
    "blue": {"primary": "#42A5F5", "secondary": "#00D1D1", "accent": "#FFD166"},
    "orange": {"primary": "#FF8C42", "secondary": "#00D1D1", "accent": "#FFD166"}
}

def detect_feed_type(csv_path=None, filename=None, data=None):
    """
    Detect feed type from:
    1. CSV feed_type column (PRIORITY)
    2. Filename keywords
    3. CSV column structure
    
    Returns: feed_type_key (str)
    """
    
    # Method 1: Check for feed_type column in CSV (HIGHEST PRIORITY)
    if data is not None and 'feed_type' in data.columns:
        feed_type_value = data['feed_type'].iloc[0] if len(data) > 0 else None
        if feed_type_value and feed_type_value in FEED_TYPES:
            return feed_type_value
    
    # Method 2: Filename detection
    if filename:
        filename_lower = filename.lower()
        for feed_key, feed_config in FEED_TYPES.items():
            for keyword in feed_config["keywords"]:
                if keyword in filename_lower:
                    return feed_key
    
    # Method 3: Column structure detection
    if data is not None:
        columns = [col.lower() for col in data.columns]
        
        # Core Equity indicators
        if any(kw in ' '.join(columns) for kw in ['refi', 'equity', 'ltv']):
            return "core_equity"
        
        # Transactional Momentum indicators
        if any(kw in ' '.join(columns) for kw in ['velocity', 'transaction', 'turnover']):
            return "transactional_momentum"
        
        # Predictive Churn indicators
        if any(kw in ' '.join(columns) for kw in ['churn', 'prediction', 'forecast']):
            return "predictive_churn"
        
        # Market Activity indicators
        if any(kw in ' '.join(columns) for kw in ['dom', 'listing', 'pricing']):
            return "market_activity"
        
        # Lender Engagement indicators
        if any(kw in ' '.join(columns) for kw in ['lender', 'rate', 'volume']):
            return "lender_engagement"
    
    # Default fallback
    return "core_equity"

def get_feed_config(feed_type):
    """
    Get configuration for a specific feed type
    
    Args:
        feed_type (str): Feed type key
        
    Returns:
        dict: Feed configuration
    """
    return FEED_TYPES.get(feed_type, FEED_TYPES["core_equity"])

def get_page_list(feed_type):
    """
    Get list of pages for a specific feed type
    
    Args:
        feed_type (str): Feed type key
        
    Returns:
        list: Page identifiers
    """
    config = get_feed_config(feed_type)
    return config["pages"]

def get_color_theme(feed_type):
    """
    Get color theme for a specific feed type
    
    Args:
        feed_type (str): Feed type key
        
    Returns:
        dict: Color theme
    """
    config = get_feed_config(feed_type)
    theme_key = config.get("color_theme", "teal")
    return COLOR_THEMES.get(theme_key, COLOR_THEMES["teal"])

def should_render_page(page_id, feed_type):
    """
    Check if a specific page should be rendered for this feed type
    
    Args:
        page_id (str): Page identifier
        feed_type (str): Feed type key
        
    Returns:
        bool: True if page should be rendered
    """
    page_list = get_page_list(feed_type)
    return page_id in page_list

# Example usage
if __name__ == "__main__":
    # Test detection
    print("Testing feed type detection:")
    print(f"Filename 'core_equity_raleigh.csv': {detect_feed_type(filename='core_equity_raleigh.csv')}")
    print(f"Filename 'churn_prediction.csv': {detect_feed_type(filename='churn_prediction.csv')}")
    
    # Test configuration
    feed_type = "predictive_churn"
    config = get_feed_config(feed_type)
    print(f"\nFeed Type: {config['name']}")
    print(f"Pages: {config['pages']}")
    print(f"Colors: {get_color_theme(feed_type)}")