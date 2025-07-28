# test_charts.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chart_utils import get_available_charts, get_campaign_data

def test_chart_functionality():
    """Test the chart functionality."""
    print("🧪 Testing Chart Functionality...")
    
    # Test 1: Check available charts
    print("📊 Available chart types:")
    charts = get_available_charts()
    for chart in charts:
        print(f"  - {chart}")
    
    # Test 2: Check if we can fetch campaign data
    print("\n📈 Testing campaign data fetch...")
    df = get_campaign_data()
    if df is not None and not df.empty:
        print(f"✅ Successfully fetched {len(df)} campaigns")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"📊 Sample data:")
        print(df.head(3))
    else:
        print("❌ Failed to fetch campaign data")
    
    # Test 3: Test chart creation (without display)
    print("\n🎨 Testing chart creation...")
    try:
        from chart_utils import create_audience_by_topic_chart
        fig = create_audience_by_topic_chart()
        if fig:
            print("✅ Audience by topic chart created successfully")
        else:
            print("❌ Failed to create audience by topic chart")
    except Exception as e:
        print(f"❌ Error creating chart: {e}")

if __name__ == "__main__":
    test_chart_functionality() 