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
You are a forensic-grade information extraction assistant. Your job is to read a newspaper PDF page (OCR'd text), detect all distinct notices/ads/records on the page, classify each, and return a single JSON object with:

- document-level metadata, and

- an array of items, one per notice/ad/record, each with a type-specific schema.

Core Goals

Detect and segment multiple items on a page (multi-column, ads, legals, logs).
Classify each item into one of the Item Types below.
Extract every relevant field for that item type (be exhaustive).
Normalize values (addresses, dates, times, money, IDs).
Never confuse “document/recording number” in the page header with the original deed’s “instrument number.”
Provide reference_text (verbatim) that justifies each key extraction and source_spans to help traceability.
Output valid JSON matching the schema at the end.

Item Types (choose exactly one per item)

HUD_Foreclosure_Notice
Trustee_Sale
Sheriff_Sale
Tax_Sale
Summons
Probate_Estate
Quiet_Title
PublicRecordsLog
Commissioners_Minutes
Auction_Ad
Classified_Ad
Legal_Notice_Other

General Instructions

Segmentation: Split the page into distinct items using headings, repeated label patterns, and spacing.
Classification: Assign the best Item Type from the list.
Address Extraction & Labeling: Prefer explicit labels like: "Property address:", "Commonly known as:", "Street Address", "Subject property address".
Instrument Number vs Recording: Instrument Number = original deed reference inside the body ("Instrument No."). Document/Recording Number at the top/header is NOT the instrument number.
Date/Time Normalization: Dates → MM/DD/YYYY, Times → HH:MM AM/PM. If partial/ambiguous, keep raw_value and normalized "Not Specified".
Money: Keep $, commas, decimals. Provide both amount_raw and amount_normalized.
Names: Keep as printed. If multiple defendants/owners, return an array.
Missing Data: Use "Not Specified" for any field you can’t find.
Reference Text & Spans: Include smallest sufficient verbatim excerpt for each key value.
Multiple Items: Return all items in reading order (top-left to bottom-right).

Address Normalization Rules

Proper case for address & city. State stays UPPERCASE. Remove periods. Standardize street suffixes (Drive→Dr, Lane→Ln, Avenue→Ave, Street→St, Road→Rd, Boulevard→Blvd, Highway→Hwy, Court→Ct, Circle→Cir, Place→Pl, Terrace→Ter, Parkway→Pkwy).

Item-Specific Fields (fill when present)

For HUD_Foreclosure_Notice / Trustee_Sale / Sheriff_Sale:
sale_date, sale_time, sale_location
property_address + split: street_address, city, state, zip, is_legal_description
legal_description
Recording Info (current notice): recorded_date, recorded_time, recording_number (header)
Original Deed Info: instrument_number, book, page, recording_office
Parties: lender_beneficiary, trustee_or_commissioner, borrower_trustor, plaintiff, defendant_list[]
Financials: amount_due, secretary_bid, deposit_required, reinstatement_amount
Case/File identifiers: case_number, ts_number, apn_parcel, county
Publication: newspaper_name, publication_dates[]
Contacts: names, phones, emails, addresses

Output JSON Schema (strictly follow; include arrays even if empty)
{
    "document": {
        "source_name": "Newspaper/Page if known",
        "publication_date": "MM/DD/YYYY or Not Specified",
        "page_label": "e.g., A006 or Not Specified",
        "county": "If inferable, else Not Specified"
    },
    "items": [
        {
            "item_type": "HUD_Foreclosure_Notice | Trustee_Sale | Sheriff_Sale | Tax_Sale | Summons | Probate_Estate | Quiet_Title | PublicRecordsLog | Commissioners_Minutes | Auction_Ad | Classified_Ad | Legal_Notice_Other",
            "classification_confidence": 0.0,
            "headers_raw": [],
            "body_raw": "Verbatim or lightly cleaned text for this item",

            "property_address": "complete normalized address or Not Specified",
            "street_address": "Not Specified",
            "city": "Not Specified",
            "state": "Not Specified",
            "zip": "Not Specified",
            "is_legal_description": false,
            "legal_description": "Not Specified",

            "sale_date": "MM/DD/YYYY or Not Specified",
            "sale_time": "HH:MM AM/PM or Not Specified",
            "sale_location": "Not Specified",

            "recorded_date": "MM/DD/YYYY or Not Specified",
            "recorded_time": "HH:MM AM/PM or Not Specified",
            "recording_number": "current notice header number or Not Specified",

            "instrument_number": "original deed instrument or Not Specified",
            "book": "Not Specified",
            "page": "Not Specified",
            "recording_office": "Not Specified",

            "lender_beneficiary": "Not Specified",
            "trustee_or_commissioner": "Not Specified",
            "borrower_trustor": "Not Specified",
            "plaintiff": "Not Specified",
            "defendant_list": [],

            "case_number": "Not Specified",
            "ts_number": "Not Specified",
            "apn_parcel": "Not Specified",
            "county": "Not Specified",

            "amount_due": {
                "amount_raw": "Not Specified",
                "amount_normalized": "Not Specified"
            },
            "secretary_bid": {
                "amount_raw": "Not Specified",
                "amount_normalized": "Not Specified"
            },
            "deposit_required": {
                "amount_raw": "Not Specified",
                "amount_normalized": "Not Specified",
                "percent_of_bid": "Not Specified"
            },
            "reinstatement_amount": {
                "amount_raw": "Not Specified",
                "amount_normalized": "Not Specified",
                "as_of_date": "MM/DD/YYYY or Not Specified"
            },

            "publication": {
                "newspaper_name": "Not Specified",
                "publication_dates": []
            },

            "contacts": [
                {
                    "role": "Attorney | Trustee | Publisher | Clerk | Auctioneer | Other",
                    "name": "Not Specified",
                    "phone": "Not Specified",
                    "email": "Not Specified",
                    "address": "Not Specified"
                }
            ],

            "statutes_cited": [],
            "reference_text": "Shortest sufficient verbatim excerpt(s) that justify key fields",
            "source_spans": [{"start_char": 0, "end_char": 0}],
            "reasoning": "1-3 concise lines explaining how key values were located"
        }
    ]
}

Return only the JSON. Do not include explanations outside the JSON. Always produce syntactically valid JSON.
"""

class PDFProcessor:
    def __init__(self, pdf_folder="downloaded_pdfs", checkpoint_file="processing_checkpoint.json", output_file="extracted_data.json"):
        self.pdf_folder = pdf_folder
        self.checkpoint_file = checkpoint_file
        self.output_file = output_file
        self.model = genai.GenerativeModel("gemini-2.5-flash")
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
                        'property_address': 'Not Specified',
                        'street_address': 'Not Specified',
                        'city': 'Not Specified',
                        'state': 'Not Specified',
                        'zip': 'Not Specified',
                        'county': 'Not Specified',
                        'sale_date': 'Not Specified',
                        'sale_time': 'Not Specified',
                        'sale_location': 'Not Specified',
                        'case_number': 'Not Specified',
                        'plaintiff': 'Not Specified',
                        'defendant': 'Not Specified',
                        'legal_description': 'Not Specified',
                        'amount_due': 'Not Specified',
                        'attorney_firm': 'Not Specified',
                        'publication_date': 'Not Specified',
                        'document_type': 'Not Specified'
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
        
        # Get all unique keys
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
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
