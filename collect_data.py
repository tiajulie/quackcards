import requests
from bs4 import BeautifulSoup
import json
import time

# Key MotherDuck pages to scrape
motherduck_urls = [
    "hhttps://motherduck.com/docs/getting-started/e2e-tutorial/part-1/",
    "https://motherduck.com/docs/getting-started/e2e-tutorial/part-2/",
    "https://motherduck.com/docs/getting-started/e2e-tutorial/part-3/",
    "https://motherduck.com/docs/getting-started/data-warehouse/",
    "https://motherduck.com/docs/getting-started/customer-facing-analytics/",
    "https://motherduck.com/docs/getting-started/interfaces/client-apis/connect-query-from-python/installation-authentication/",
    "https://motherduck.com/docs/getting-started/interfaces/client-apis/connect-query-from-python/choose-database/",
    "https://motherduck.com/docs/getting-started/interfaces/client-apis/connect-query-from-python/loading-data-into-md/",
    "https://motherduck.com/docs/getting-started/interfaces/client-apis/connect-query-from-python/querying-data/",
    "https://motherduck.com/docs/getting-started/interfaces/connect-query-from-duckdb-cli/",
    "https://motherduck.com/docs/getting-started/interfaces/motherduck-quick-tour/",
    "https://motherduck.com/docs/getting-started/interfaces/motherduck-web-ui/",
    "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/sql-assistant/prompt-query/",
    "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/sql-assistant/prompt-sql/",
    "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/sql-assistant/prompt-explain/",
    "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/sql-assistant/prompt-fix-line/",
    "https://motherduck.com/docs/sql-reference/motherduck-sql-reference/ai-functions/prompt/",

]

def scrape_motherduck_docs():
    print("🦆 Scraping MotherDuck documentation...")
    docs_data = []
    
    for url in motherduck_urls:
        try:
            print(f"Scraping: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Hackathon Bot)'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get main content (adjust selectors based on site structure)
                title = soup.find('title').get_text() if soup.find('title') else url
                content = soup.get_text()
                
                # Clean up whitespace
                content = ' '.join(content.split())
                
                docs_data.append({
                    "source": "motherduck_docs",
                    "url": url,
                    "title": title,
                    "content": content[:8000],  # Limit to 8k chars per page
                    "length": len(content)
                })
                
                time.sleep(1)  # Be nice to their servers
            else:
                print(f"Failed to scrape {url}: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    
    # Save to file
    with open('motherduck_docs.json', 'w') as f:
        json.dump(docs_data, f, indent=2)
    
    print(f"✅ Saved {len(docs_data)} documentation pages")
    return docs_data

if __name__ == "__main__":
    docs = scrape_motherduck_docs()