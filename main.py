import logging
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import io
import os
from datetime import datetime
from logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add any other origins you want to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BATCH_SIZE = 100  # Define the batch size for processing

# Set up Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_service = ChromeService(executable_path='./chromedriver.exe')  # Update with your path to ChromeDriver

def extract_info(driver):
    """
    Extracts the required information from the Selenium driver and returns it as a dictionary.
    Customize the extraction logic based on the specific website structure.
    """
    info = {}

    try:
        # Example: Extracting elements based on class names and CSS selectors
        # Update the logic to match the specific structure of the target website

        # Extract example element (replace with actual logic)
        example_element = driver.find_element(By.CLASS_NAME, 'example-class-name')
        info['example'] = example_element.text.strip() if example_element else 'N/A'

        # Add other elements as needed
        # ...

    except Exception as e:
        logger.error(f"Error extracting information: {e}")
        info = {
            'example': 'N/A',
            # Add other elements as needed
            # ...
        }
    
    return info

def scrape_details(url: str) -> dict:
    """
    Scrapes the details from the provided URL using Selenium.
    
    Args:
    url (str): The URL of the page to scrape.
    
    Returns:
    dict: A dictionary containing the extracted details.
    """
    try:
        logger.info(f"Scraping details for URL: {url}")
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get(url)
        
        # Extract the relevant information
        info = extract_info(driver)
        
        # Log the extracted information for easier inspection
        logger.debug(f"Extracted information: {info}")

        driver.quit()
        return info
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {e}")
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/scrape")
def scrape_details_endpoint(url: str):
    """
    Endpoint to scrape details from a single URL.
    
    Usage:
    GET /scrape?url=<URL>
    
    Args:
    url (str): The URL of the page to scrape.
    
    Returns:
    dict: A dictionary containing the extracted details.
    """
    logger.info(f"Scraping details for URL: {url}")
    return scrape_details(url)

@app.post("/scrape_all")
async def scrape_all_details(file: UploadFile = File(...)):
    """
    Endpoint to scrape details from multiple URLs provided in a CSV file.
    
    Usage:
    POST /scrape_all
    Form Data: file (Upload a CSV file with a column named `url`)
    
    Args:
    file (UploadFile): The uploaded CSV file containing the URLs to scrape.
    
    Returns:
    dict: A dictionary containing the message and the file path of the saved results.
    """
    try:
        logger.info(f"Received file: {file.filename}")
        # Read the uploaded file
        contents = await file.read()
        # Use StringIO to treat the bytes as a file-like object
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        if 'url' not in df.columns:
            logger.error("CSV file must contain a 'url' column")
            raise HTTPException(status_code=400, detail="CSV file must contain a 'url' column")

        # Prepare output file
        output_filename = f"scraped_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        output_filepath = os.path.join(os.path.dirname(__file__), output_filename)

        # Initialize results DataFrame
        results_df = pd.DataFrame(columns=['url', 'example', 'error'])
        
        # Process in batches
        for start in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[start:start + BATCH_SIZE]
            batch_results = []

            for index, row in batch.iterrows():
                url = row['url']
                try:
                    details = scrape_details(url)
                    batch_results.append({
                        'url': url,
                        **details
                    })
                except HTTPException as e:
                    logger.warning(f"Skipping URL due to error: {url} - {e.detail}")
                    batch_results.append({
                        'url': url,
                        'example': 'N/A',
                        'error': e.detail
                    })
            
            # Append batch results to the results DataFrame
            results_df = pd.concat([results_df, pd.DataFrame(batch_results)], ignore_index=True)

            # Save intermediate results to CSV
            results_df.to_csv(output_filepath, index=False)
            logger.info(f"Saved batch results to {output_filepath}")

        return {"message": "Scraping completed", "file_path": output_filepath}
    except Exception as e:
        logger.error(f"Unexpected error during file processing: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/download")
def download_file(file_path: str):
    """
    Endpoint to download the specified file.
    
    Args:
    file_path (str): The path to the file to be downloaded.
    
    Returns:
    FileResponse: The file to be downloaded.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=os.path.basename(file_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
