from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
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
titles = []
descriptions = []
images = []
prices = []
ratings = []
sizes_list = []
brands = []
genders = []
in_stock_list=[]
categories = []

try:
    for url in products:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 1. Title
        title = soup.title.text if soup.title else "Title not found"
        titles.append(title)

        # 2. Description
        prod_desc_section = soup.find('section', class_='prod-desc')
        if prod_desc_section:
            details = []
            detail_list_items = prod_desc_section.find_all('li')
            for item in detail_list_items:
                detail_text = item.get_text(separator=" ")
                details.append(detail_text)
        # Join all details into a single string with new lines separating each detail
            full_description = "\n".join(details)
            descriptions.append(full_description)
        else:
            descriptions.append("Description section not found.")

        # 3. Images
        img_tags = soup.find_all('img', class_="img-alignment")
        img_urls = []
        for i in img_tags:
            src = i.get('src')
            if src:
                img_urls.append(src)
        img_urls_str = ", ".join(img_urls)
        images.append(img_urls_str)

        # 4. Price
        price_detail = soup.find('div', class_="prod-sp")
        if price_detail:
                price_text = price_detail.text
        else:
            price_text = "Price details element not found."
        prices.append(price_text)


        # 5. Rating
        rating = soup.find('span', class_='_1p6Xx')
        if rating:
              rating_text= rating.text
        else:
            rating_text="Rating not found."
        ratings.append(rating_text)

        # 6. Sizes
        sizes = soup.find_all('div', class_="size-swatch")
        size_texts = []
        for size in sizes:
            size_text = size.text.strip()
            size_texts.append(size_text)
        sizes_list.append(size_texts)


        # 7. Brand
        brandname = soup.find('h2', class_="brand-name")
        if brandname:
            brand_text = brandname.text
        else:
            brand_text = "Brand name not found."
        brands.append(brand_text)


        # 8. Gender
        gender = "Not specified"
        breadcrumb = soup.find('ul', class_='breadcrumb-sec')
        if breadcrumb:
            text = breadcrumb.get_text().lower()
            if any(keyword in text for keyword in ['men', 'male', 'man', 'gentlemen']):
                gender = "Men"
            elif any(keyword in text for keyword in ['women', 'female', 'woman', 'ladies']):
                gender = "Women"
        genders.append(gender)

        # 9.IN_Stock
        in_stock_statuses = []
        size_variant_items = soup.find_all('div', class_='size-variant-item')

        for item in size_variant_items:
            if 'size-instock' in item['class']:
                    in_stock_statuses.append('In Stock')
            else:
                    in_stock_statuses.append('Out of Stock')
        in_stock_list.append(in_stock_statuses)

        # 10. Category
        parent_category = "Parent category not found"
        child_category = "Child category not found"
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all('li')
            if len(breadcrumb_items) >= 2:
                parent_category = breadcrumb_items[-2].get_text().strip()
            if len(breadcrumb_items) >= 3:
                child_category = breadcrumb_items[-3].get_text().strip()
        categories.append(f"{parent_category} > {child_category}")


        
finally:
    driver.quit()

# Create DataFrame
data = {
    'Title': titles,
    'Description': descriptions,
    'Images': images,
    'Price': prices,
    'Rating': ratings,
    'Sizes': sizes_list,
    'Brand': brands,
    'Gender': genders,
    'in_stock_statuses':in_stock_list,
    'Category': categories
    }

df = pd.DataFrame(data)

# Save DataFrame to CSV
df.to_csv('scraped_data.csv', index=False)

print("Data saved to scraped_data.csv")


