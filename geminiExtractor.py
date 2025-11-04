import json
import os
import time
from datetime import datetime
import google.generativeai as genai
import re
from modules.logger import Logger
from modules.mailer import Mailer
from dotenv import load_dotenv

load_dotenv()
Logger = Logger()
Mailer = Mailer()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEST = bool(os.getenv("TEST"))


class GeminiExtractor:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Enhanced Gemini prompt for Hennepin County foreclosure property extraction
        self.gemini_prompt = """
You are a helpful assistant designed to extract property information from Hennepin County foreclosure case documents. 

Extract the following information from the document text:

1. **Property Address** - Look for property address, legal address, or premises address
2. **City** - Extract city name from the property address  
3. **State** - Extract state from the property address (use MN for Minnesota)
4. **ZIP Code** - Extract ZIP/postal code from the property address
5. **County** - Look for "County", "COUNTY", or county references (typically Hennepin County)
6. **Sale Date** - Look for foreclosure sale date, auction date, or sheriff's sale date
7. **Sale Time** - Extract the time from the sale date information
8. **Sale Location** - Look for sale location, sheriff's office, courthouse, etc.
9. **Amount Due** - Look for judgment amount, debt amount, or amount owed
10. **Defendant/Owner** - Look for defendant name or property owner name
11. **Case Number** - Look for court case number or file number
12. **Legal Description** - Extract the legal property description if available

**Important Instructions:**
- Focus on the PROPERTY being foreclosed, not attorney addresses
- For Minnesota properties, use "MN" as the state abbreviation
- Extract exact dates and times as written
- Include dollar signs and formatting for amounts
- For Hennepin County, look for "Hennepin County, Minnesota"
- If information is not found, use "Not Specified"

**Format your response as a JSON object with these exact keys:**
{
    "property_address": "complete property address or Not Specified",
    "city": "city name or Not Specified", 
    "state": "MN or other state abbreviation or Not Specified",
    "zip": "zip code or Not Specified",
    "county": "county name or Not Specified",
    "sale_date": "foreclosure sale date or Not Specified",
    "sale_time": "sale time or Not Specified", 
    "sale_location": "sale venue/location or Not Specified",
    "amount_due": "judgment/debt amount with $ or Not Specified",
    "defendant_owner": "defendant or owner name or Not Specified",
    "case_number": "court case number or Not Specified",
    "legal_description": "legal description or Not Specified"
}

**Example patterns to look for:**
- "Property Address: 1234 Main Street, Minneapolis, MN 55401"
- "Foreclosure Sale Date: December 15, 2025 at 10:00 AM"  
- "Location: Hennepin County Sheriff's Office"
- "Judgment Amount: $150,000.00"
- "Defendant: John Smith"
- "Case No: 27-CV-24-12345"

Always return valid JSON format.
"""

    def clean_json_string(self, text: str) -> str:
        """Clean and extract JSON from Gemini response"""
        try:
            # Look for JSON object in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in response")
            
            json_str = json_match.group()
            # Remove any markdown formatting
            json_str = re.sub(r'```json\s*|\s*```', '', json_str)
            return json_str
        except Exception as e:
            Logger.error(f"Error cleaning JSON: {e}")
            return None

    def process_with_gemini(self, description_text, record_id, retry_count=0, max_retries=3):
        """Process description text with Gemini AI to extract property information with retry logic"""
        try:
            # Combine the description with the prompt
            full_prompt = f"Document Text:\n{description_text}\n\n{self.gemini_prompt}"
            
            response = self.model.generate_content(full_prompt)
            if not response.text:
                if retry_count < max_retries:
                    Logger.log(f"Empty response, retrying ({retry_count + 1}/{max_retries})...")
                    time.sleep(5)  # Wait 5 seconds before retry
                    return self.process_with_gemini(description_text, record_id, retry_count + 1, max_retries)
                else:
                    raise Exception("Empty response from Gemini after all retries")
            
            # Clean and parse JSON response
            json_str = self.clean_json_string(response.text)
            if not json_str:
                if retry_count < max_retries:
                    Logger.log(f"Invalid JSON response, retrying ({retry_count + 1}/{max_retries})...")
                    time.sleep(5)  # Wait 5 seconds before retry
                    return self.process_with_gemini(description_text, record_id, retry_count + 1, max_retries)
                else:
                    raise Exception("Invalid JSON response after all retries")
            
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['property_address', 'city', 'state', 'zip', 'county', 'sale_date', 
                             'sale_time', 'sale_location', 'amount_due', 'defendant_owner',
                             'case_number', 'legal_description']
            
            for field in required_fields:
                if field not in result:
                    result[field] = "Not Specified"
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            Logger.error(f"Error processing with Gemini for {record_id}: {error_msg}")
            
            # Check if it's a rate limit error or quota exceeded
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if retry_count < max_retries:
                    wait_time = 60 * (retry_count + 1)  # Exponential backoff: 60s, 120s, 180s
                    Logger.log(f"Rate limit hit, waiting {wait_time} seconds before retry ({retry_count + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    return self.process_with_gemini(description_text, record_id, retry_count + 1, max_retries)
                else:
                    Logger.error(f"Rate limit exceeded after {max_retries} retries. Stopping processing.")
                    raise Exception(f"Rate limit exceeded after {max_retries} retries")
            else:
                # For other errors, retry with shorter wait
                if retry_count < max_retries:
                    Logger.log(f"API error, retrying ({retry_count + 1}/{max_retries})...")
                    time.sleep(10)  # Wait 10 seconds for other errors
                    return self.process_with_gemini(description_text, record_id, retry_count + 1, max_retries)
                else:
                    raise Exception(f"API error after {max_retries} retries: {error_msg}")

    def get_default_result(self):
        """Return default result structure for cases with insufficient description data"""
        return {
            'property_address': 'Not Specified',
            'city': 'Not Specified', 
            'state': 'Not Specified',
            'zip': 'Not Specified',
            'county': 'Not Specified',
            'sale_date': 'Not Specified',
            'sale_time': 'Not Specified',
            'sale_location': 'Not Specified',
            'amount_due': 'Not Specified',
            'defendant_owner': 'Not Specified',
            'case_number': 'Not Specified',
            'legal_description': 'Not Specified'
        }

    def extract_info_from_text(self, description_text, record_id="unknown"):
        """Main method to extract property information from text - standardized interface"""
        try:
            if not description_text or len(description_text) < 50:
                Logger.log("Warning: Description too short or empty")
                return self.get_default_result()
            
            Logger.log(f"Extracting property info with Gemini AI...")
            start_time = time.time()
            
            # This will handle retries internally and raise exception if all retries fail
            result = self.process_with_gemini(description_text, record_id)
            process_time = time.time() - start_time
            Logger.log(f"Processed in {process_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            Logger.error(f"Failed to extract property info: {e}")
            Mailer.send_mail(
                "Error In Hennepin County Gemini Extractor",
                f"Error extracting property info for {record_id}: {e}",
            )
            return self.get_default_result()