import re
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Initialize lists to store the extracted data
firm_names = []
websites = []
emails = []
phones = []
address_1_list = []
address_2_list = []
address_3_list = []
descriptions = []

# Base URL pattern
base_url = "https://www.danskeark.dk/find-arkitekt?page="

# Loop through pages 0 to 27
for page_num in range(0, 28):
    # Construct the URL for the current page
    url = base_url + str(page_num)
    
    # Request the page with explicit encoding
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure response is read with UTF-8 encoding
    soup = BeautifulSoup(response.text, "html.parser")

    # Parse firms on the current page
    for entry in soup.select('.views-row'):
        # Firm Name
        firm_name = entry.find("h3", class_="title").get_text(strip=True)
        firm_names.append(firm_name)
        
        # Description
        summary = entry.find("p", class_="content-summary").get_text(strip=True) if entry.find("p", class_="content-summary") else ""
        body = entry.find("div", class_="content-body").get_text(strip=True) if entry.find("div", class_="content-body") else ""
        descriptions.append(summary + " " + body)
        
        # Contact Information
        contact_box = entry.find("div", class_="contact-box")
        
        # Address split into address_1, address_2, address_3 based on <br>
        if contact_box:
            # Decode the HTML and split by <br> tags
            address_html = contact_box.find("div", class_="column").decode_contents().strip()
            address_parts = [part.strip() for part in address_html.split("<br/>")]
            if len(address_parts) < 3:
                address_parts += [""] * (3 - len(address_parts))  # Ensure there are exactly 3 parts
        else:
            address_parts = ["", "", ""]
        
        # Assign each part to address_1, address_2, and address_3
        address_1_list.append(address_parts[0])
        address_2_list.append(address_parts[1])
        address_3_list.append(address_parts[2])
        
        # Phone using regex to capture phone number format
        phone = ""
        if contact_box:
            phone_match = re.search(r"\b\d{8,10}\b", contact_box.get_text())
            phone = phone_match.group() if phone_match else ""
        phones.append(phone)
        
        # Email
        email = contact_box.find("a", href=lambda href: href and "mailto:" in href).get("href").replace("mailto:", "") if contact_box and contact_box.find("a", href=lambda href: href and "mailto:" in href) else ""
        emails.append(email)
        
        # Website
        website = contact_box.find("a", href=lambda href: href and "http" in href).get("href") if contact_box and contact_box.find("a", href=lambda href: href and "http" in href) else ""
        websites.append(website)

    print(f"Finished scraping page {page_num}")

# Create a DataFrame
data = pd.DataFrame({
    "firm_name": firm_names,
    "website": websites,
    "email": emails,
    "phone": phones,
    "address_1": address_1_list,
    "address_2": address_2_list,
    "address_3": address_3_list,
    "description": descriptions
})

# Export to CSV with UTF-8 encoding and BOM (Byte Order Mark)
data.to_csv("firms_data.csv", index=False, encoding="utf-8-sig")
print("Data exported to firms_data.csv")
