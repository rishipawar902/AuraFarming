#!/usr/bin/env python3
"""
AGMARKNET Website Investigation Tool
Analyzes the current structure and requirements of the AGMARKNET website.
"""

import httpx
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime

async def investigate_agmarknet():
    """Investigate the current AGMARKNET website structure."""
    
    print("🔍 Investigating AGMARKNET Website Structure")
    print("=" * 60)
    
    base_url = "https://agmarknet.gov.in"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
        
        # 1. Check homepage
        print("\n📱 Step 1: Checking homepage...")
        try:
            home_response = await client.get(f"{base_url}/default.aspx")
            print(f"Homepage status: {home_response.status_code}")
            
            if home_response.status_code == 200:
                soup = BeautifulSoup(home_response.content, 'html.parser')
                
                # Look for search/price related links
                print("\n🔗 Found links:")
                links = soup.find_all('a', href=True)
                price_links = [link for link in links if any(keyword in link.get('href', '').lower() or keyword in link.get_text().lower() 
                             for keyword in ['price', 'search', 'market', 'commodity', 'mandi', 'report'])]
                
                for i, link in enumerate(price_links[:10]):  # Show first 10 relevant links
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if href and text:
                        print(f"   {i+1}. {text} -> {href}")
                
                # Look for forms
                print("\n📝 Found forms:")
                forms = soup.find_all('form')
                for i, form in enumerate(forms):
                    action = form.get('action', 'N/A')
                    method = form.get('method', 'GET')
                    print(f"   Form {i+1}: {method} -> {action}")
                    
                    # Look for form inputs
                    inputs = form.find_all(['input', 'select'])
                    for inp in inputs[:5]:  # Show first 5 inputs
                        name = inp.get('name', '')
                        inp_type = inp.get('type', inp.name)
                        if name:
                            print(f"      - {inp_type}: {name}")
                
        except Exception as e:
            print(f"❌ Error checking homepage: {e}")
        
        # 2. Try direct search page access
        print("\n📊 Step 2: Checking search page...")
        search_urls = [
            "/SearchCmmMkt.aspx",
            "/search.aspx", 
            "/prices.aspx",
            "/reports.aspx",
            "/SearchCommodity.aspx"
        ]
        
        for url in search_urls:
            try:
                full_url = f"{base_url}{url}"
                print(f"\nTrying: {full_url}")
                response = await client.get(full_url)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check for state/district dropdowns
                    selects = soup.find_all('select')
                    for select in selects:
                        name = select.get('name', '')
                        if any(keyword in name.lower() for keyword in ['state', 'district', 'commodity']):
                            print(f"   Found dropdown: {name}")
                            options = select.find_all('option')[:5]  # First 5 options
                            for opt in options:
                                value = opt.get('value', '')
                                text = opt.get_text(strip=True)
                                if text and text != '--Select--':
                                    print(f"      {value}: {text}")
                    
                    # Look for Jharkhand references
                    text_content = soup.get_text().lower()
                    if 'jharkhand' in text_content:
                        print("   ✅ Found Jharkhand references!")
                    
                elif response.status_code == 302:
                    location = response.headers.get('location', 'No location header')
                    print(f"   Redirects to: {location}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # 3. Try alternative approach - look for API endpoints
        print("\n🔌 Step 3: Looking for API endpoints...")
        api_patterns = [
            "/api/",
            "/data/",
            "/json",
            "/xml",
            "/service",
            "/webservice"
        ]
        
        for pattern in api_patterns:
            try:
                response = await client.get(f"{base_url}{pattern}")
                if response.status_code == 200:
                    print(f"✅ Found potential API: {pattern}")
            except:
                pass
        
        # 4. Check for JavaScript that might contain endpoint URLs
        print("\n🔧 Step 4: Checking for JavaScript endpoints...")
        try:
            home_response = await client.get(f"{base_url}/default.aspx")
            if home_response.status_code == 200:
                soup = BeautifulSoup(home_response.content, 'html.parser')
                scripts = soup.find_all('script')
                
                for script in scripts:
                    if script.string:
                        # Look for URL patterns in JavaScript
                        js_content = script.string
                        urls = re.findall(r'["\']([^"\']*\.aspx[^"\']*)["\']', js_content)
                        if urls:
                            print("   Found URLs in JavaScript:")
                            for url in set(urls)[:5]:  # Unique URLs, max 5
                                print(f"      {url}")
                
        except Exception as e:
            print(f"❌ Error checking JavaScript: {e}")

if __name__ == "__main__":
    asyncio.run(investigate_agmarknet())
