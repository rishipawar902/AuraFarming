"""
Debug AGMARKNET response to see actual data structure
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

async def debug_agmarknet():
    """Debug what AGMARKNET actually returns"""
    
    print("🔍 DEBUGGING AGMARKNET RESPONSE")
    print("=" * 50)
    
    async with httpx.AsyncClient(
        timeout=30.0,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        follow_redirects=True
    ) as client:
        
        # Step 1: Get the main page
        main_response = await client.get("https://agmarknet.gov.in/default.aspx")
        print(f"Main page status: {main_response.status_code}")
        
        # Step 2: Parse and submit form
        soup = BeautifulSoup(main_response.text, 'html.parser')
        
        # Find form data
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        
        form_data = {
            '__VIEWSTATE': viewstate['value'] if viewstate else '',
            '__EVENTVALIDATION': eventvalidation['value'] if eventvalidation else '',
            'ctl00$MainContent$ddlMarket': '23',  # Ranchi code
            'ctl00$MainContent$btnSubmit': 'Go'
        }
        
        # Step 3: Submit form
        form_response = await client.post("https://agmarknet.gov.in/default.aspx", data=form_data)
        print(f"Form submission status: {form_response.status_code}")
        print(f"Redirected to: {form_response.url}")
        
        # Step 4: Get the search page with commodity data
        search_url = str(form_response.url)
        search_response = await client.get(search_url)
        print(f"Search page status: {search_response.status_code}")
        
        # Step 5: Parse the response to see actual content
        soup = BeautifulSoup(search_response.text, 'html.parser')
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n--- TABLE {i+1} ---")
            rows = table.find_all('tr')
            print(f"Table has {len(rows)} rows")
            
            for j, row in enumerate(rows[:5]):  # Show first 5 rows
                cells = row.find_all(['td', 'th'])
                if cells:
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"Row {j+1}: {cell_texts}")
            
            if len(rows) > 5:
                print(f"... and {len(rows)-5} more rows")
        
        # Look for specific price-related content
        price_elements = soup.find_all(text=lambda x: x and ('price' in x.lower() or 'rate' in x.lower() or '₹' in x))
        print(f"\nFound {len(price_elements)} price-related elements:")
        for elem in price_elements[:10]:
            print(f"  - {elem.strip()}")
        
        # Look for commodity names
        commodity_elements = soup.find_all(text=lambda x: x and any(crop in x.lower() for crop in ['rice', 'wheat', 'potato', 'onion']))
        print(f"\nFound {len(commodity_elements)} commodity elements:")
        for elem in commodity_elements[:10]:
            print(f"  - {elem.strip()}")

if __name__ == "__main__":
    asyncio.run(debug_agmarknet())
