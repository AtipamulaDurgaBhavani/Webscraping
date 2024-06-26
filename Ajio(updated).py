from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import re
import pandas as pd

webdriver_path = 'C:\\chromedriver-win64\\chromedriver.exe'  
# Set up the Selenium WebDriver
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)

products = [
    "https://www.ajio.com/search/?text=464501984005",
    "https://www.ajio.com/search/?text=465069433001",
    "https://www.ajio.com/search/?text=441140715003",
    "https://www.ajio.com/search/?text=465156487008",
    "https://www.ajio.com/search/?text=464498909004",
    "https://www.ajio.com/search/?text=420178164003",
    "https://www.ajio.com/search/?text=469034006001",
    "https://www.ajio.com/search/?text=410312978012",
    "https://www.ajio.com/search/?text=441130178008",
    "https://www.ajio.com/search/?text=463669997005"
]

# Lists to store data
ids = [] 
titles = []
descriptions = []
images = []
prices = []
ratings = []
sizes_list = []
brands = []
genders = []
in_stock_list = []
parent_categories = []
child_categories = []

try:
    for url in products:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # product ID
        product_id = url.split('=')[-1]  # Split the URL by '=' and take the last part
        ids.append(product_id)

        # 1. Title
        title_tag = soup.find('h1', class_='prod-name')
        if title_tag:
            title = title_tag.text.strip()
        else:
            title = None
        titles.append(title)

        # 2. Description
        prod_desc_section = soup.find('section', class_='prod-desc')
        if prod_desc_section:
            details = [item.get_text(separator=" ").strip() for item in prod_desc_section.find_all('li')]
            full_description = "\n".join(details)
            descriptions.append(full_description)
        else:
            descriptions.append(None)

        # 3. Images
        img_tags = soup.find_all('img', class_="img-alignment")
        img_urls = [img.get('src') for img in img_tags if img.get('src')]
        img_urls_str = ", ".join(img_urls)
        images.append(img_urls_str)

        # 4. Price
        def extract_price(price_text):
            match = re.search(r'\d+(\.\d+)?', price_text.replace(',', ''))
            if match:
                return int(float(match.group()))  # Convert to float and then to int
            return None
        
        selling_price_detail = soup.find('div', class_="prod-sp")
        if selling_price_detail:
            selling_price_text = selling_price_detail.text.strip()
            selling_price = extract_price(selling_price_text)
        else:
            selling_price = None
        prices.append(selling_price)

        
        # 5. Rating
        rating_tag = soup.find('span', class_='_1p6Xx')
        rating = rating_tag.text.strip() if rating_tag else None
        ratings.append(rating)

        # 6. Sizes
        sizes = soup.find_all('div', class_="size-swatch")
        size_texts = [size.text.strip() for size in sizes]
        sizes_list.append(size_texts)

        # 7. Brand
        brandname = soup.find('h2', class_="brand-name")
        brand_text = brandname.text.strip() if brandname else None
        brands.append(brand_text)

       # 8. Gender
        gender = None
        breadcrumb = soup.find('ul', class_='breadcrumb-sec')
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all('li')
            breadcrumb_text = [item.get_text().strip().lower() for item in breadcrumb_items]
            print(f"Breadcrumb items: {breadcrumb_text}")  
            if any('women' in item for item in breadcrumb_text):
                gender = "Women"
            elif any('men' in item for item in breadcrumb_text):
                gender = "Men"
        genders.append(gender)
        print(f"Gender detected: {gender}")  

         
        
        # 9. In Stock Status
        in_stock_statuses = []
        size_variant_items = soup.find_all('div', class_='size-variant-item')
        for item in size_variant_items:
            if 'size-instock' in item['class']:
                in_stock_statuses.append('In Stock')
            else:
                in_stock_statuses.append('Out of Stock')
        in_stock_list.append(in_stock_statuses)

        # 10. Category
        parent_category = None
        child_category = None
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all('li')
            if len(breadcrumb_items) >= 2:
                parent_category = breadcrumb_items[-2].get_text().strip()
            if len(breadcrumb_items) >= 3:
                child_category = breadcrumb_items[-3].get_text().strip()
        parent_categories.append(parent_category)
        child_categories.append(child_category)

finally:
    driver.quit()


lengths = [
    len(ids), len(titles), len(descriptions), len(images), len(prices),
     len(ratings), len(sizes_list), len(brands), len(genders),
    len(in_stock_list), len(parent_categories), len(child_categories)
]

if len(set(lengths)) == 1:
    # Create DataFrame
    data = {
        'ID': ids, 
        'Title': titles,
        'Description': descriptions,
        'Images': images,
        'Price': prices, 
        'Rating': ratings,
        'Sizes': sizes_list,
        'Brand': brands,
        'Gender': genders,
        'In Stock Statuses': in_stock_list,
        'Parent Category': parent_categories,
        'Child Category': child_categories
    }

    df = pd.DataFrame(data)

    # Save DataFrame to CSV
    df.to_csv('scraped_data.csv', index=False)

    print("Data saved to scraped_data.csv")

