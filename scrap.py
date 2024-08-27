from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Load the main documentation page
url = "https://www.iobroker.net/#en/documentation/config/cli.md"
driver.get(url)

# Wait for the page to fully render
time.sleep(5)

# Parse the main page to find links to all subpages
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract all links that lead to documentation subpages
# We'll look for specific anchors that link to documentation sections
doc_links = soup.find_all('a', href=True)

# Filter and construct full URLs for subpages
subpage_urls = []
for link in doc_links:
    href = link['href']
    # Only consider links that are part of the documentation section
    if "/documentation/" in href or href.startswith("#en/documentation"):
        if href.startswith("http"):  # If it's already a full URL
            subpage_urls.append(href)
        else:  # Construct full URL for relative links
            full_url = url.split("#")[0] + href.replace("#en", "")
            subpage_urls.append(full_url)

# Initialize a variable to hold all scraped content
all_formatted_data = ""

# Visit each subpage and scrape the content
for page_url in subpage_urls:
    print(f"Scraping {page_url}")
    driver.get(page_url)
    time.sleep(5)  # Wait for the subpage to fully load
    page_soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract and structure the content
    content = page_soup.find_all(['h1', 'h2', 'h3', 'p', 'code'])
    structured_data = []
    for tag in content:
        if tag.name.startswith('h'):
            structured_data.append({'type': 'header', 'level': int(tag.name[1]), 'content': tag.get_text()})
        elif tag.name == 'p':
            structured_data.append({'type': 'text', 'content': tag.get_text()})
        elif tag.name == 'code':
            structured_data.append({'type': 'code', 'content': tag.get_text()})

    # Format the data from this subpage
    formatted_data = ""
    for item in structured_data:
        if item['type'] == 'header':
            formatted_data += "#" * item['level'] + " " + item['content'] + "\n\n"
        elif item['type'] == 'text':
            formatted_data += item['content'] + "\n\n"
        elif item['type'] == 'code':
            formatted_data += "```\n" + item['content'] + "\n```\n\n"

    # Append to the overall content
    all_formatted_data += formatted_data

# Close the browser
driver.quit()

# Write all the scraped content to a file
file_name = "iobrokerdocs.txt"
with open(file_name, 'w', encoding='utf-8') as file:
    file.write(all_formatted_data)

print(f"All documentation has been written to {file_name}")
