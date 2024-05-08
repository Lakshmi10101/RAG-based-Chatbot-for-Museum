import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the division with the specified id and class
            division = soup.find('div', {'id': 'col-157638099', 'class': 'col collectionDataHolder medium-9 small-12 large-10'})
            if division:    
                # Find all links within the division
                links = division.find_all('a', href=True)
                
                # Extract URLs and scrape content from each link
                content = []
                
                for link in links:
                    absolute_url = url + link['href'] if link['href'].startswith('/') else link['href']
                    link_content = scrape_page_content(absolute_url)
                    if link_content:
                        content.append(link_content)
                return "\n\n".join(content)
            else:
                print("Division not found.")
                return None
        else:
            print("Failed to fetch the landing page.")
            return None
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def scrape_page_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the division with the specified class
            division = soup.find('div', {'class': 'large-6 col'})
            if division:
                # Extract text content
                content = division.get_text(' | ', strip=True)
                return content
            else:
                print("Division not found.")
                return None
        else:
            print(f"Failed to fetch the page at {url}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    landing_page_url = "https://csmvs.in/all-collections/collection-indian-decorative-art-or-sculptures-or-textiles-and-costumes-of-india/objecttype-architectural-fragment/"
    output_file = "website_content.txt"
    
    # Scrape content from the landing page
    content = scrape_website(landing_page_url)
    if content:
        # Write scraped content to the output file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(content)
            print(f"Scraped content saved to {output_file}")
