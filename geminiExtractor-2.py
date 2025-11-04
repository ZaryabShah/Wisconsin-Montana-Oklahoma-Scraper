import re
import os
import base64
import json
import google.generativeai as genai
from modules.logger import Logger
from dotenv import load_dotenv
import time

Logger = Logger()


PROMPT = """
You are a helpful assistant designed to extract the property address from foreclosure case documents. Your task is to look for property address labels and extract the address that immediately follows. Look for various forms of address labels including but not limited to:

- "Property address"
- "The street address and other common designation"
- "Street address"
- "Address"
- "Property location"
- "Subject property address"
- Or similar variations that clearly indicate the physical property address

### Instructions:
1. Search for any of the above address labels (case-insensitive) followed by a colon, dash, or other punctuation. If found, extract the address that immediately follows this label.
2. Ensure that the extracted address is the one associated with the property under foreclosure, not an address of another party.
3. If none of these address labels are found, do not attempt to extract addresses from phrases like 'the subject property,' 'the mortgaged premises,' or 'the property described herein.' Instead, indicate that no property address was found.
4. Do not extract addresses associated with the plaintiff, defendant, attorney, or other parties.
5. **Extract Sale Date and Time**: Look for sale date/time information typically found in phrases like "on [date] at [time]", "will occur at public auction", "scheduled date of the sale", etc.
6. **Extract Recording Information**: Look for recording date and time, often found at the top of the document or in phrases like "recorded on", "eRECORDED IN OFFICIAL RECORDS", etc.
7. **Extract Instrument Number**: Look for the ORIGINAL instrument number mentioned in the deed of trust content, typically found in phrases like "Instrument No.", "Instrument Number", "as Instrument No.", "recorded as Instrument", or "Deed of Trust dated [date], recorded as Instrument No. [number]". DO NOT use the document number or recording number from the header/top of the document - find the instrument number that refers to the original deed of trust being foreclosed.

### Interpretation of is_legal_description:
- Set `is_legal_description` to `true` only when the text following the "Property address" label is a legal description (e.g., lot numbers, block numbers, or condominium unit descriptions, such as 'LOT 51 AND 52, BLOCK 3320, UNIT 65, CAPE CORAL' or 'CONDOMINIUM UNIT NO. 402, IN BEAU RIVAGE').
- Set `is_legal_description` to `false` when the text following the "Property address" label is a physical address (e.g., '602 HARRISON DR LEHIGH ACRES FL 33936') or when no "Property address" label is found.

### Formatting Rules:
1. Convert the entire address to proper case (e.g., CHANDLER → Chandler), except for the state abbreviation, which should remain in uppercase (e.g., AZ).
2. Remove all periods from the address.
3. Use commas as separators between address components.
4. Standardize street types as follows:
   - Drive → Dr
   - Lane → Ln
   - Avenue → Ave
   - Street → St
   - Road → Rd
Example:
Before: 4342 W. PORT AU PRINCE LN, GLENDALE, AZ 85306
After: 4342 W Port Au Prince Ln, Glendale, AZ 85306

### Handling Missing Data:
1. If a physical address follows the "Property address" label but one or more components (street address, city, state, or zip) are missing, use 'Not Specified' for the missing component(s) while retaining the valid components. Set `is_legal_description` to `false`.
2. If a legal description follows the "Property address" label, use 'Not Specified' for all address fields (`property_address`, `street_address`, `city`, `state`, `zip`) and set `is_legal_description` to `true`.
3. If the "Property address" line is not found, use 'Not Specified' for all address fields and set `is_legal_description` to `false`.

### Reference Text and Reasoning:
1. If the "Property address" line is found, include the exact paragraph or sentence from the document where the property address or legal description was extracted in the `reference_text` field.
2. If the address or legal description spans multiple sentences or lines following the label, include the relevant continuous text block.
3. Ensure the `reference_text` clearly shows the context of the extracted address or legal description.
4. Provide a brief explanation in the `reasoning` field, such as whether a physical address or legal description was found via the "Property address" label or if the label was absent.

### JSON Schema:
```json
{
    "property_address": "complete address",
    "street_address": "Street Address",
    "city": "City",
    "state": "State",
    "zip": "ZIP",
    "sale_date": "Sale Date (MM/DD/YYYY format)",
    "sale_time": "Sale Time (HH:MM AM/PM format)",
    "recorded_date": "Recorded Date (MM/DD/YYYY format)", 
    "recorded_time": "Recorded Time (HH:MM AM/PM format)",
    "instrument_number": "Instrument Number from document",
    "is_legal_description": false,
    "reference_text": "exact paragraph or sentence from the document",
    "reasoning": "explanation for the output"
}
```

### Example Input 1 (With "Property address" Line, Physical Address):
Document containing: 'Property address: 602 HARRISON DR LEHIGH ACRES FL 33936'

### Example Output 1:
```json
{
    "property_address": "602 Harrison Dr, Lehigh Acres, FL 33936",
    "street_address": "602 Harrison Dr",
    "city": "Lehigh Acres",
    "state": "FL",
    "zip": "33936",
    "sale_date": "01/27/2026",
    "sale_time": "11:30 AM",
    "recorded_date": "10/17/2025",
    "recorded_time": "09:06 AM",
    "instrument_number": "20232690397",
    "is_legal_description": false,
    "reference_text": "Property address: 602 HARRISON DR LEHIGH ACRES FL 33936",
    "reasoning": "The document explicitly states the physical address following the 'Property address' label."
}
```

### Example Input 2 (With "Property address" Line, Missing City):
Document containing: 'Property address: 18331/335 DURRANCE RD, FL 33917'

### Example Output 2:
```json
{
    "property_address": "18331/335 Durrance Rd, Not Specified, FL 33917",
    "street_address": "18331/335 Durrance Rd",
    "city": "Not Specified",
    "state": "FL",
    "zip": "33917",
    "sale_date": "Not Specified",
    "sale_time": "Not Specified",
    "recorded_date": "Not Specified",
    "recorded_time": "Not Specified",
    "instrument_number": "Not Specified",
    "is_legal_description": false,
    "reference_text": "Property address: 18331/335 DURRANCE RD, FL 33917",
    "reasoning": "The document provides a physical address following the 'Property address' label but lacks the city component."
}
```

### Example Input 3 (With "Property address" Line, Missing ZIP):
Document containing: 'Property address: 1234 CORAL AVE, CAPE CORAL, FL'

### Example Output 3:
```json
{
    "property_address": "1234 Coral Ave, Cape Coral, FL Not Specified",
    "street_address": "1234 Coral Ave",
    "city": "Cape Coral",
    "state": "FL",
    "zip": "Not Specified",
    "sale_date": "Not Specified",
    "sale_time": "Not Specified",
    "recorded_date": "Not Specified",
    "recorded_time": "Not Specified",
    "instrument_number": "Not Specified",
    "is_legal_description": false,
    "reference_text": "Property address: 1234 CORAL AVE, CAPE CORAL, FL",
    "reasoning": "The document provides a physical address following the 'Property address' label but lacks the ZIP code."
}
```

### Example Input 4 (With "Property address" Line, Legal Description):
Document containing: 'Property address: LOT 51 AND 52, BLOCK 3320, UNIT 65, CAPE CORAL, ACCORDING TO THE PLAT THEREOF RECORDED IN PLAT BOOK 21, PAGES 151 THROUGH 164, INCLUSIVE, PUBLIC RECORDS OF PIMA COUNTY, ARIZONA.'

### Example Output 4:
```json
{
    "property_address": "Not Specified",
    "street_address": "Not Specified",
    "city": "Not Specified",
    "state": "Not Specified",
    "zip": "Not Specified",
    "is_legal_description": true,
    "reference_text": "Property address: LOT 51 AND 52, BLOCK 3320, UNIT 65, CAPE CORAL, ACCORDING TO THE PLAT THEREOF RECORDED IN PLAT BOOK 21, PAGES 151 THROUGH 164, INCLUSIVE, PUBLIC RECORDS OF PIMA COUNTY, ARIZONA.",
    "reasoning": "The document provides a legal description following the 'Property address' label, so no physical address was extracted."
}
```

### Example Input 5 (With "The street address and other common designation" Label):
Document containing: 'The street address and other common designation: 789 Pine St, Naples, FL 34103.'

### Example Output 5:
```json
{
    "property_address": "789 Pine St, Naples, FL 34103",
    "street_address": "789 Pine St",
    "city": "Naples",
    "state": "FL",
    "zip": "34103",
    "is_legal_description": false,
    "reference_text": "The street address and other common designation: 789 Pine St, Naples, FL 34103.",
    "reasoning": "The document provides a physical address following the 'The street address and other common designation' label."
}
```

### Example Input 6 (Without Any Address Label, Only Legal Description):
Document containing: 'The property described herein as CONDOMINIUM UNIT NO. 402, IN BEAU RIVAGE, A CONDOMINIUM, ACCORDING TO THE DECLARATION THEREOF, RECORDED OCTOBER 18, 2004 IN OFFICIAL RECORDS BOOK 4468, AT PAGE 73, OF THE PUBLIC RECORDS OF PIMA COUNTY, ARIZONA.'

### Example Output 6:
```json
{
    "property_address": "Not Specified",
    "street_address": "Not Specified",
    "city": "Not Specified",
    "state": "Not Specified",
    "zip": "Not Specified",
    "is_legal_description": false,
    "reference_text": "No property address found in the document.",
    "reasoning": "The document does not contain any recognized address labels, so no address was extracted."
}
```

### Example Input 7 (No Address or Legal Description):
Document containing: 'This is a notice of Lis Pendens for a foreclosure action against John Doe. No specific property details are provided in this document.'

### Example Output 7:
```json
{
    "property_address": "Not Specified",
    "street_address": "Not Specified",
    "city": "Not Specified",
    "state": "Not Specified",
    "zip": "Not Specified",
    "is_legal_description": false,
    "reference_text": "No property address found in the document.",
    "reasoning": "The document does not contain any recognized address labels, so no address was extracted."
}
```

### IMPORTANT NOTE - Instrument Number Distinction:
DO NOT confuse the document recording number (found at the top of the document) with the instrument number. 
- Document/Recording Number: Usually at the top (e.g., "20252830504") - this is for the current notice of sale document
- Instrument Number: Found in the content referring to the original deed of trust (e.g., "Deed of Trust dated 9/26/2023, recorded as Instrument No. 20232690397") - this is what you should extract

### Example Input 8 (Instrument Number Clarification):
Document containing: 'Header shows: 20252830504. Content shows: The following legally described trust property will be sold, pursuant to the power of sale under that certain Deed of Trust dated 9/26/2023, recorded on 9/26/2023, as Instrument No. 20232690397'

### Example Output 8:
```json
{
    "property_address": "Not Specified",
    "street_address": "Not Specified", 
    "city": "Not Specified",
    "state": "Not Specified",
    "zip": "Not Specified",
    "sale_date": "Not Specified",
    "sale_time": "Not Specified",
    "recorded_date": "Not Specified",
    "recorded_time": "Not Specified",
    "instrument_number": "20232690397",
    "is_legal_description": false,
    "reference_text": "Deed of Trust dated 9/26/2023, recorded on 9/26/2023, as Instrument No. 20232690397",
    "reasoning": "Found the original deed of trust instrument number (20232690397) in the content, not the document header number (20252830504)."
}
```
"""

class GeminiExtractor:
    def __init__(self):
        load_dotenv()
        # Use the provided API key
        genai.configure(api_key="")
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def clean_json_string(self, text: str) -> str:
        """Clean and extract JSON from the response text."""
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response")
        json_str = json_match.group()
        json_str = re.sub(r"```json\s*|\s*```", "", json_str)
        return json_str

    def extract_info_from_pdf_ns(self, pdf_path):
        try:
            with open(pdf_path, "rb") as doc_file:
                doc_data = base64.standard_b64encode(doc_file.read()).decode("utf-8")
            response = None
            response = self.model.generate_content(
                [{"mime_type": "application/pdf", "data": doc_data}, PROMPT]
            )
            if not response.text:
                Logger.error(f"Empty response from Gemini for {pdf_path} - {response}")
                return None
            Logger.ai_response(f"Extracted TEXT for {pdf_path} - {response.text}")
            json_str = self.clean_json_string(response.text)
            return json.loads(json_str)
        except Exception as e:
            Logger.error(f"Failed to process PDF: {str(e)} - {pdf_path} - {response}")
            time.sleep(5)
            return {
                "property_address": "",
                "street_address": "",
                "city": "",
                "state": "",
                "zip": "",
                "sale_date": "",
                "sale_time": "",
                "recorded_date": "",
                "recorded_time": "",
                "instrument_number": "",
            }