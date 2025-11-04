# pip install curl_cffi==0.6.*
import json
import re
from pathlib import Path
from curl_cffi import requests
from urllib.parse import urljoin, unquote

# Configuration
INPUT_FILE = "output.json"
OUTPUT_DIR = Path("downloaded_pdfs")
BASE_URL = "https://usbbe01.newsmemory.com"

HEADERS = {
    "accept": "application/pdf,*/*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://opa.eclipping.org/",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

def extract_pdf_links(data):
    """Extract PDF download links and metadata from the JSON data."""
    pdf_info = []
    
    for idx, record in enumerate(data.get("aaData", [])):
        if len(record) < 2:
            continue
        
        # Extract newspaper name from first column
        newspaper_match = re.search(r'<strong>(.*?)</strong>', record[0])
        newspaper = newspaper_match.group(1) if newspaper_match else f"Unknown_{idx}"
        
        # Extract date and page from second column
        date_match = re.search(r'<strong>date</strong>:\s*(\d{2}/\d{2}/\d{4})', record[1])
        page_match = re.search(r'<strong>page</strong>:\s*(\w+)', record[1])
        
        date = date_match.group(1).replace('/', '-') if date_match else "unknown_date"
        page = page_match.group(1) if page_match else "unknown_page"
        
        # Extract PDF download link
        pdf_link_match = re.search(r'href="(//usbbe01\.newsmemory\.com/eebrowser/bbe_prod/[^"]+)"', record[1])
        
        if pdf_link_match:
            pdf_url = "https:" + pdf_link_match.group(1)
            
            # Create a clean filename
            clean_newspaper = re.sub(r'[^\w\s-]', '', newspaper).strip().replace(' ', '_')
            filename = f"{clean_newspaper}_{date}_page_{page}.pdf"
            
            pdf_info.append({
                'url': pdf_url,
                'filename': filename,
                'newspaper': newspaper,
                'date': date,
                'page': page,
                'index': idx
            })
    
    return pdf_info

def download_pdf(session, pdf_data, output_dir):
    """Download a single PDF file."""
    url = pdf_data['url']
    filename = pdf_data['filename']
    filepath = output_dir / filename
    
    try:
        print(f"📥 Downloading: {pdf_data['newspaper']} - {pdf_data['date']} (Page {pdf_data['page']})")
        print(f"   URL: {url}")
        
        response = session.get(url, timeout=60)
        response.raise_for_status()
        
        # Check if response is actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and response.content[:4] != b'%PDF':
            print(f"   ⚠️  Warning: Response may not be a PDF (Content-Type: {content_type})")
        
        # Save the file
        filepath.write_bytes(response.content)
        file_size = len(response.content) / 1024  # Size in KB
        print(f"   ✅ Saved: {filename} ({file_size:.2f} KB)")
        return True
        
    except Exception as e:
        print(f"   ❌ Error downloading {filename}: {e}")
        return False

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR.resolve()}\n")
    
    # Load JSON data
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE} not found!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return
    
    # Extract PDF links
    pdf_list = extract_pdf_links(data)
    
    if not pdf_list:
        print("❌ No PDF links found in the data!")
        return
    
    print(f"🔍 Found {len(pdf_list)} PDF(s) to download\n")
    print("=" * 80)
    
    # Download PDFs
    success_count = 0
    failed_count = 0
    
    with requests.Session(impersonate="chrome120") as session:
        session.headers.update(HEADERS)
        
        for pdf_data in pdf_list:
            if download_pdf(session, pdf_data, OUTPUT_DIR):
                success_count += 1
            else:
                failed_count += 1
            print()  # Empty line between downloads
    
    # Summary
    print("=" * 80)
    print(f"\n📊 Download Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📁 Files saved to: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
