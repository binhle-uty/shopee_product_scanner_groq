# shopee_product_scanner_groq
Using groq and langchain LLM to scan the product to list the category and sub-category.

# Requirements
```bash
pip install -r requirements.txt
```

# Running code
```bash
python script.py
```

# Step by step:
- Step 1: Control the Google Sheet Path
- Step 2: Register the Groq API to get key
- Step 3: Create `.env`file with groq API Keys with this format 
GROQ_API_KEY="grod_api_key"
- Step 4: Run the script.py

# TODO:
1) Moving from Google Sheets to Supabase
2) Get the running chunking to overcome limitations of Groq API
