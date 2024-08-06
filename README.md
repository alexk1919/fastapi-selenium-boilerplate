# Generic Web Scraping API with FastAPI and Selenium

This is a generic FastAPI application designed for web scraping using Selenium. It can be customized to scrape data from any website by updating the HTML element extraction logic.

## Features

- Scrape details from a single URL
- Scrape details from multiple URLs provided in a CSV file
- Save the scraped results to a CSV file
- Logging with file rotation

## Requirements

- Python 3.7+
- Google Chrome
- ChromeDriver

## Installation
1. **Clone the repository:**

   ```bash
   git clone https://github.com/alexk1919/fastapi-selenium-boilerplate.git
   cd fastapi-selenium-boilerplate

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Customization
To customize the scraping logic for a specific website, update the extract_info function in main.py to match the structure of the target website's HTML.

## Logging
Logs are saved to app.log with rotation after 10MB. The logging configuration is set up in logging_config.py.

## License
This project is licensed under the MIT License.