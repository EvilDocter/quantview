import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = "https://www.google.com/finance/quote/HDFCBANK:NSE"
r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.text, 'html.parser')

# Save raw HTML for analysis
with open("/tmp/gf_hdfcbank.html", "w") as f:
    f.write(r.text)

# Find all divs with class names that contain data
print("=== All class-named divs with short text ===")
seen_texts = set()
for div in soup.find_all('div'):
    classes = div.get('class', [])
    text = div.get_text(strip=True)
    # Only leaf divs with meaningful short text
    if classes and text and len(text) < 60 and not div.find('div'):
        key = f"{' '.join(classes)}: {text}"
        if key not in seen_texts:
            seen_texts.add(key)
            # Only show financial-looking data
            if any(c in text for c in ['₹', '%', '.', 'Cr', 'cap', 'P/E', 'EPS', 'Div', 'yield', 'Vol', 'High', 'Low']):
                print(f"  [{' '.join(classes)}] {text}")

# Look for the stats table structure
print("\n=== Looking for structured data rows ===")
# Google Finance uses specific class patterns for data rows
for row_div in soup.find_all('div'):
    children = row_div.find_all('div', recursive=False)
    if len(children) == 2:
        left = children[0].get_text(strip=True)
        right = children[1].get_text(strip=True)
        if left and right and len(left) < 30 and len(right) < 30:
            if any(kw in left.lower() for kw in ['prev', 'high', 'low', 'cap', 'p/e', 'eps', 'div', 'yield', 'vol', '52', 'open']):
                print(f"  {left} -> {right}")

# Extract from the raw text
print("\n=== Raw text around keywords ===")
text = soup.get_text(separator="\n")
lines = text.split("\n")
for i, line in enumerate(lines):
    line = line.strip()
    if line and any(kw in line.lower() for kw in ['previous close', 'day range', 'year range', 'market cap', 'p/e ratio', 'dividend yield', 'primary exchange']):
        context = lines[max(0,i-1):min(len(lines),i+3)]
        print(f"  Line {i}: {[l.strip() for l in context if l.strip()]}")
