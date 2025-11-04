import os
import json
import csv
import base64
import time
from datetime import datetime
import google.generativeai as genai
from pathlib import Path
import re

# Configure Gemini AI
genai.configure(api_key="")

PROMPT = """
You are a specialized extraction assistant for foreclosure and legal notices from newspaper PDFs. Extract property and foreclosure information with precision.

### ⚠️ CRITICAL INSTRUCTION - PHYSICAL ADDRESS PRIORITY:
**When a document contains BOTH a legal description AND a "Commonly known as:" address:**
- ALWAYS extract the "Commonly known as:" address as the property address
- IGNORE the legal description for address fields
- The "Commonly known as:" line contains the actual street address where the property is located
- Example: If you see both "Legal Description: Lot 4, Block 8..." AND "Commonly known as: 207 Texas Street, Hooker, OK 73945"
  → Extract: "207 Texas St, Hooker, OK 73945" (NOT the legal description)

### PRIMARY EXTRACTION RULES:

**1. PROPERTY ADDRESS EXTRACTION (CRITICAL - PRIORITY ORDER):**
   - **FIRST PRIORITY**: Look for "Commonly known as:" - this usually contains the PHYSICAL street address
   - **SECOND PRIORITY**: Look for other address labels: "Property address:", "Street address:", "Subject property address:", "The street address and other common designation:", "Property location:"
   - **PHYSICAL ADDRESS vs LEGAL DESCRIPTION**:
     * PHYSICAL ADDRESS contains: house number, street name, city, state, zip (e.g., "207 Texas Street, Hooker, OK 73945")
     * LEGAL DESCRIPTION contains: lot numbers, blocks, units, additions, plat references (e.g., "Lot 4, Block 8, Baker Brothers Addition")
   - **EXTRACTION RULES**:
     * If "Commonly known as:" is found with a physical address → ALWAYS extract that address
     * If only legal description is found → set is_legal_description=true, use "Not Specified" for all address fields
     * Extract the PROPERTY being foreclosed, NOT attorney/plaintiff/defendant/courthouse addresses
     * NEVER extract legal descriptions into address fields
   - If NO physical address found, use "Not Specified" for all address fields

**2. ADDRESS NORMALIZATION:**
   - Convert to proper case (e.g., HOOKER → Hooker), EXCEPT state stays UPPERCASE (OK, MN, FL, etc.)
   - Remove all periods from addresses
   - Standardize suffixes: Drive→Dr, Lane→Ln, Avenue→Ave, Street→St, Road→Rd, Boulevard→Blvd, Highway→Hwy, Court→Ct, Circle→Cir, Place→Pl, Terrace→Ter, Parkway→Pkwy
   - Use commas to separate components
   - Example: "207 TEXAS STREET, HOOKER, OK 73945" → "207 Texas St, Hooker, OK 73945"

**3. DATE EXTRACTION & FORMATTING:**
   - ALL dates MUST be in MM/DD/YYYY format
   - Auction/Sale Date: Look for "sale date", "auction date", "sheriff's sale", "foreclosure sale on [date]"
   - Posted/Recorded Date: Look for "recorded on", "recorded date", "eRECORDED", "publication date", document header recording info
   - Redemption Expiration Date: Look for "redemption period", "right of redemption expires", "redemption deadline"
   - Convert all date formats to MM/DD/YYYY (e.g., "July 30, 2025" → "07/30/2025", "06-05-2025" → "06/05/2025")

**4. TIME EXTRACTION:**
   - Extract auction/sale time in HH:MM AM/PM format
   - Look for phrases like "at 10:00 AM", "10:00 a.m.", "11:30 AM"

**5. FINANCIAL AMOUNTS:**
   - Amount of Judgment: Look for "judgment amount", "amount due", "debt amount", "principal balance"
   - Final Bid Amount: Look for "final bid", "winning bid", "secretary will bid", "HUD will bid"
   - Deposit Amount: Look for "deposit required", "deposit totaling", "earnest money"
   - Amount Due: Total amount owed including principal, interest, fees
   - Extract as numbers with $ symbol (e.g., "$121,291.18")

**6. CASE NUMBER:**
   - Look for "Case No.", "Case Number", "Cause No.", "TS No.", "File No.", "Docket No."
   - Examples: "CJ-2024-38", "27-CV-24-12345", "TS No. 53-3325-OK", "PB-2025-25"

**7. INSTRUMENT NUMBER (CRITICAL):**
   - Extract the ORIGINAL deed of trust instrument number from document CONTENT
   - Look for phrases: "Instrument No.", "Instrument Number", "recorded as Instrument No.", "as Instrument", "Deed of Trust dated [date], recorded as Instrument No. [number]"
   - DO NOT use the document/recording number from the page HEADER
   - Example: Content says "recorded as Instrument No. 20232690397" → extract "20232690397"

**8. NOTICE TITLE/TYPE:**
   - Classify the notice type: "HUD Foreclosure Notice", "Sheriff's Sale", "Trustee Sale", "Tax Sale", "Foreclosure Notice", "Notice of Default", "Auction", "Probate Estate", "Summons", etc.

**9. COUNTY:**
   - Extract county name from addresses, legal descriptions, or court information
   - Examples: "Texas County", "Kay County", "Lincoln County", "Hennepin County"

**10. MISSING DATA:**
   - Use "Not Specified" for any field not found in the document
   - If partial address available, use "Not Specified" for missing components

### OUTPUT JSON SCHEMA (REQUIRED FIELDS ONLY):
```json
{
    "full_address": "complete normalized PHYSICAL address or Not Specified",
    "notice_title": "type of notice/document or Not Specified",
    "street_address": "street address only or Not Specified",
    "city": "city name or Not Specified",
    "county": "county name or Not Specified",
    "state": "STATE ABBREVIATION or Not Specified",
    "zip": "zip code or Not Specified",
    "auction_date": "MM/DD/YYYY or Not Specified",
    "posted_date": "MM/DD/YYYY or Not Specified",
    "case_number": "case/file number or Not Specified",
    "amount_of_judgment": "$XXX,XXX.XX or Not Specified",
    "auction_time": "HH:MM AM/PM or Not Specified",
    "redemption_expiration_date": "MM/DD/YYYY or Not Specified",
    "final_bid_amount": "$XXX,XXX.XX or Not Specified",
    "deposit_amount": "$XXX,XXX.XX or Not Specified",
    "amount_due": "$XXX,XXX.XX or Not Specified",
    "instrument_number": "original deed instrument number or Not Specified",
    "legal_description": "lot/block/plat legal description or Not Specified",
    "is_legal_description": false
}
```

**CRITICAL RULE FOR LEGAL DESCRIPTIONS:**
- If the property info contains ONLY legal description (lots, blocks, plats), set:
  - `full_address` = "Not Specified"
  - `street_address` = "Not Specified" 
  - `city` = "Not Specified" (unless explicitly stated separately)
  - `state` = extract from legal description
  - `zip` = "Not Specified"
  - `legal_description` = the full legal description text
  - `is_legal_description` = true
- NEVER put legal description text in the `full_address` field!

### EXAMPLES:

**Example 1 - HUD Foreclosure with Full Data:**
Input: "Commonly known as: 207 Texas Street, Hooker, OK 73945. Sale Date: July 30, 2025 at 10:00 AM. Amount Due: $121,291.18. Case No: TS No. 53-3325-OK. Recorded as Instrument No. I-2011-001086."

Output:
```json
{
    "full_address": "207 Texas St, Hooker, OK 73945",
    "notice_title": "HUD Foreclosure Notice",
    "street_address": "207 Texas St",
    "city": "Hooker",
    "county": "Texas County",
    "state": "OK",
    "zip": "73945",
    "auction_date": "07/30/2025",
    "posted_date": "Not Specified",
    "case_number": "TS No. 53-3325-OK",
    "amount_of_judgment": "$121,291.18",
    "auction_time": "10:00 AM",
    "redemption_expiration_date": "Not Specified",
    "final_bid_amount": "Not Specified",
    "deposit_amount": "Not Specified",
    "amount_due": "$121,291.18",
    "instrument_number": "I-2011-001086",
    "is_legal_description": false
}
```

**Example 2 - Legal Description (No Physical Address):**
Input: "Property address: LOT 51 AND 52, BLOCK 3320, CAPE CORAL, ACCORDING TO PLAT BOOK 21. Sale: 06/15/2025 at 11:00 AM."

Output:
```json
{
    "full_address": "Not Specified",
    "notice_title": "Foreclosure Sale",
    "street_address": "Not Specified",
    "city": "Not Specified",
    "county": "Not Specified",
    "state": "Not Specified",
    "zip": "Not Specified",
    "auction_date": "06/15/2025",
    "posted_date": "Not Specified",
    "case_number": "Not Specified",
    "amount_of_judgment": "Not Specified",
    "auction_time": "11:00 AM",
    "redemption_expiration_date": "Not Specified",
    "final_bid_amount": "Not Specified",
    "deposit_amount": "Not Specified",
    "amount_due": "Not Specified",
    "instrument_number": "Not Specified",
    "legal_description": "LOT 51 AND 52, BLOCK 3320, CAPE CORAL, ACCORDING TO PLAT BOOK 21",
    "is_legal_description": true
}
```

**Example 3 - Document with BOTH Legal Description AND Physical Address:**
Input: "Legal Description: All of Lot Four (4) in Block Eight (8) in Baker Brothers North side Addition to the Town of Hooker, Texas County, Oklahoma. Commonly known as: 207 Texas Street, Hooker, OK 73945. Sale Date: July 30, 2025 at 10:00 AM. Instrument No. I-2011-001086. Amount Due: $121,291.18."

Output:
```json
{
    "full_address": "207 Texas St, Hooker, OK 73945",
    "notice_title": "Foreclosure Sale",
    "street_address": "207 Texas St",
    "city": "Hooker",
    "county": "Texas County",
    "state": "OK",
    "zip": "73945",
    "auction_date": "07/30/2025",
    "posted_date": "Not Specified",
    "case_number": "Not Specified",
    "amount_of_judgment": "Not Specified",
    "auction_time": "10:00 AM",
    "redemption_expiration_date": "Not Specified",
    "final_bid_amount": "Not Specified",
    "deposit_amount": "Not Specified",
    "amount_due": "$121,291.18",
    "instrument_number": "I-2011-001086",
    "is_legal_description": false
}
```

**Example 4 - Sheriff's Sale with Deposit:**
Input: "**Example 3 - Sheriff's Sale with Deposit:**
Input: "Property: 108 Maple Drive, Kaw City, OK 74641. Sheriff's Sale on June 30, 2025 at 11:00 AM. Judgment: $126,703.85. Deposit required: 10% of bid. Case CJ-2024-001."

Output:
```json
{
    "full_address": "108 Maple Dr, Kaw City, OK 74641",
    "notice_title": "Sheriff's Sale",
    "street_address": "108 Maple Dr",
    "city": "Kaw City",
    "county": "Kay County",
    "state": "OK",
    "zip": "74641",
    "auction_date": "06/30/2025",
    "posted_date": "Not Specified",
    "case_number": "CJ-2024-001",
    "amount_of_judgment": "$126,703.85",
    "auction_time": "11:00 AM",
    "redemption_expiration_date": "Not Specified",
    "final_bid_amount": "Not Specified",
    "deposit_amount": "10% of bid",
    "amount_due": "$126,703.85",
    "instrument_number": "Not Specified",
    "legal_description": "Not Specified",
    "is_legal_description": false
}
```"

Output:
```json
{
    "full_address": "108 Maple Dr, Kaw City, OK 74641",
    "notice_title": "Sheriff's Sale",
    "street_address": "108 Maple Dr",
    "city": "Kaw City",
    "county": "Kay County",
    "state": "OK",
    "zip": "74641",
    "auction_date": "06/30/2025",
    "posted_date": "Not Specified",
    "case_number": "CJ-2024-001",
    "amount_of_judgment": "$126,703.85",
    "auction_time": "11:00 AM",
    "redemption_expiration_date": "Not Specified",
    "final_bid_amount": "Not Specified",
    "deposit_amount": "10% of bid",
    "amount_due": "$126,703.85",
    "instrument_number": "Not Specified",
    "is_legal_description": false
}
```

### CRITICAL REMINDERS:
- Focus on PROPERTY address, not attorney/plaintiff addresses
- Dates MUST be MM/DD/YYYY format
- State abbreviations stay UPPERCASE
- Instrument number is from CONTENT, not header
- Use "Not Specified" for missing data
- Return ONLY valid JSON, no explanations outside JSON
"""

class PDFProcessor:
    def __init__(self, pdf_folder="downloaded_pdfs", checkpoint_file="processing_checkpoint.json", output_file="extracted_data.json"):
        self.pdf_folder = pdf_folder
        self.checkpoint_file = checkpoint_file
        self.output_file = output_file
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.processed_files = self.load_checkpoint()
        
    def load_checkpoint(self):
        """Load the checkpoint file to see which PDFs have been processed"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                return set(checkpoint.get('processed_files', []))
        return set()
    
    def save_checkpoint(self, filename):
        """Save the checkpoint after processing each file"""
        self.processed_files.add(filename)
        checkpoint = {
            'processed_files': list(self.processed_files),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        print(f"✓ Checkpoint saved: {filename}")
    
    def clean_json_string(self, text: str) -> str:
        """Clean and extract JSON from the response text"""
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")
        json_str = json_match.group()
        json_str = re.sub(r"```json\s*|\s*```", "", json_str)
        return json_str
    
    def extract_info_from_pdf(self, pdf_path, retry_count=0, max_retries=3):
        """Extract information from a PDF using Gemini AI"""
        try:
            with open(pdf_path, "rb") as doc_file:
                doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")
            
            print(f"  → Sending to Gemini AI...")
            response = self.model.generate_content(
                [{"mime_type": "application/pdf", "data": doc_data}, PROMPT]
            )
            
            if not response.text:
                if retry_count < max_retries:
                    print(f"  ⚠ Empty response, retrying ({retry_count + 1}/{max_retries})...")
                    time.sleep(5)
                    return self.extract_info_from_pdf(pdf_path, retry_count + 1, max_retries)
                else:
                    raise Exception("Empty response from Gemini after all retries")
            
            print(f"  → Parsing response...")
            json_str = self.clean_json_string(response.text)
            result = json.loads(json_str)
            
            # Add metadata
            result['source_file'] = os.path.basename(pdf_path)
            result['processed_at'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Error: {error_msg}")
            
            # Check for rate limit errors
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if retry_count < max_retries:
                    wait_time = 60 * (retry_count + 1)
                    print(f"  ⚠ Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self.extract_info_from_pdf(pdf_path, retry_count + 1, max_retries)
                else:
                    raise Exception(f"Rate limit exceeded after {max_retries} retries")
            else:
                if retry_count < max_retries:
                    print(f"  ⚠ Retrying ({retry_count + 1}/{max_retries})...")
                    time.sleep(10)
                    return self.extract_info_from_pdf(pdf_path, retry_count + 1, max_retries)
                else:
                    # Return default structure on final failure
                    return {
                        'source_file': os.path.basename(pdf_path),
                        'processed_at': datetime.now().isoformat(),
                        'error': error_msg,
                        'full_address': 'Not Specified',
                        'notice_title': 'Not Specified',
                        'street_address': 'Not Specified',
                        'city': 'Not Specified',
                        'county': 'Not Specified',
                        'state': 'Not Specified',
                        'zip': 'Not Specified',
                        'auction_date': 'Not Specified',
                        'posted_date': 'Not Specified',
                        'case_number': 'Not Specified',
                        'amount_of_judgment': 'Not Specified',
                        'auction_time': 'Not Specified',
                        'redemption_expiration_date': 'Not Specified',
                        'final_bid_amount': 'Not Specified',
                        'deposit_amount': 'Not Specified',
                        'amount_due': 'Not Specified',
                        'instrument_number': 'Not Specified',
                        'legal_description': 'Not Specified',
                        'is_legal_description': False
                    }
    
    def append_to_output(self, data):
        """Append extracted data to output file"""
        # Load existing data
        existing_data = []
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        
        # Append new data
        existing_data.append(data)
        
        # Save updated data
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    def export_to_csv(self):
        """Export JSON data to CSV format"""
        if not os.path.exists(self.output_file):
            print("No data to export to CSV")
            return
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("No data to export to CSV")
            return
        
        csv_file = self.output_file.replace('.json', '.csv')
        
        # Define the column order
        fieldnames = [
            'full_address', 'notice_title', 'street_address', 'city', 'county', 'state', 'zip',
            'auction_date', 'posted_date', 'case_number', 'amount_of_judgment', 'auction_time',
            'redemption_expiration_date', 'final_bid_amount', 'deposit_amount', 'amount_due',
            'instrument_number', 'legal_description', 'is_legal_description', 'source_file', 'processed_at'
        ]
        
        # Add any additional fields that might be present
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Add extra fields at the end
        extra_fields = sorted(list(all_keys - set(fieldnames)))
        fieldnames.extend(extra_fields)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"\n✓ CSV exported to: {csv_file}")
    
    def process_all_pdfs(self):
        """Process all PDFs in the folder"""
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_folder}")
            return
        
        print(f"\n{'='*60}")
        print(f"PDF PROCESSOR - Starting Processing")
        print(f"{'='*60}")
        print(f"Total PDFs found: {len(pdf_files)}")
        print(f"Already processed: {len(self.processed_files)}")
        print(f"Remaining to process: {len([f for f in pdf_files if f not in self.processed_files])}")
        print(f"{'='*60}\n")
        
        for idx, pdf_file in enumerate(pdf_files, 1):
            if pdf_file in self.processed_files:
                print(f"[{idx}/{len(pdf_files)}] ⊘ Skipping (already processed): {pdf_file}")
                continue
            
            print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file}")
            print(f"-" * 60)
            
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            
            try:
                # Extract data
                extracted_data = self.extract_info_from_pdf(pdf_path)
                
                # Append to output
                self.append_to_output(extracted_data)
                print(f"  ✓ Data appended to {self.output_file}")
                
                # Save checkpoint
                self.save_checkpoint(pdf_file)
                
                # Add delay to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                print(f"  ✗ Failed to process {pdf_file}: {e}")
                # Still save checkpoint to avoid retrying failed files repeatedly
                self.save_checkpoint(pdf_file)
                continue
        
        print(f"\n{'='*60}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total processed: {len(self.processed_files)}")
        print(f"Output file: {self.output_file}")
        
        # Export to CSV
        self.export_to_csv()
        
        print(f"{'='*60}\n")


def main():
    processor = PDFProcessor(
        pdf_folder="downloaded_pdfs",
        checkpoint_file="processing_checkpoint.json",
        output_file="extracted_data.json"
    )
    
    processor.process_all_pdfs()


if __name__ == "__main__":
    main()
