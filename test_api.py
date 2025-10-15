# test_api.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Starting API Test ---")

try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")

    genai.configure(api_key=api_key)

    print("API Key configured. Listing models...")

    # This is the crucial part. We are asking the API what it offers.
    model_count = 0
    for m in genai.list_models():
        # Check if the model supports the 'generateContent' method
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model found: {m.name}")
            model_count += 1
    
    if model_count > 0:
        print("\nSUCCESS: Successfully connected and found usable models.")
    else:
        print("\nWARNING: Connected, but no models supporting 'generateContent' found.")

except Exception as e:
    print(f"\nERROR: The test failed. Reason: {e}")

print("--- API Test Finished ---")