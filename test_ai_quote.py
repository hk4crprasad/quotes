#!/usr/bin/env python3
"""
Quick test script for AI quote generation
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the quote generator from test.py
from test import ViralQuoteGenerator

def test_ai_quote_generation():
    """Test AI quote generation"""
    print("🤖 Testing AI-Powered Quote Generation")
    print("=" * 50)
    
    # Initialize generator
    generator = ViralQuoteGenerator()
    
    # Test 1: Generate a basic quote
    print("\n1. Generating a basic quote:")
    try:
        quote = generator.generate_quote()
        print(f"✅ Success!")
        print(f"Title: {quote.title}")
        print(f"Content: {quote.content}")
        print(f"Theme: {quote.theme}")
        print(f"Engagement Score: {quote.engagement_score}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Generate themed quote
    print("\n2. Generating a 'relationships' themed quote:")
    try:
        quote = generator.generate_quote(theme="relationships", target_audience="empaths")
        print(f"✅ Success!")
        print(f"Title: {quote.title}")
        print(f"Content: {quote.content[:100]}{'...' if len(quote.content) > 100 else ''}")
        print(f"Theme: {quote.theme}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Check cache functionality
    print("\n3. Testing cache functionality:")
    try:
        # Generate a few quotes to populate cache
        for i in range(3):
            generator.generate_quote(theme="self-worth")
        
        # Get trending quotes
        trending = generator.get_trending_quotes(limit=5)
        print(f"✅ Cache contains {len(trending)} quotes")
        
        if trending:
            print(f"Top quote: '{trending[0].title}' (Score: {trending[0].engagement_score})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Quote Generator Test Complete!")

if __name__ == "__main__":
    test_ai_quote_generation()
