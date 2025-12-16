import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

# -------------------------------
#   MongoDB
# -------------------------------
web_url = "https://liliome.com/%D8%A8%D8%B1%D9%86%D8%AF%D9%87%D8%A7-%D8%B9%D8%B7%D8%B1-%D8%A7%D8%AF%DA%A9%D9%84%D9%86-%D9%81%D8%B1%D9%88%D8%B4%DA%AF%D8%A7%D9%87-%D8%B9%D8%B7%D8%B1-%D9%84%DB%8C%D9%84%DB%8C%D9%88%D9%85"
client = MongoClient("mongodb://localhost:27017/")
db = client["Perfume"]
brands_col = db["Brands"]
master_col = db["Master"]

# -------------------------------
#   MongoDB Indexes (RUN ONCE)
# -------------------------------
brands_col.create_index("brand_name", unique=True)
master_col.create_index(
    [("brand", 1), ("english_name", 1)],
    unique=True
)

# -------------------------------
#   Functions
# -------------------------------
def total_pages(weblink: str):
    site = requests.get(weblink)
    if not site:
        return 1

    soup = BeautifulSoup(site.text, "html.parser")
    pagination = soup.find("ul", class_="page-numbers")
    if not pagination:
        return 1

    pages = []
    for li in pagination.find_all("li"):
        try:
            pages.append(int(li.get_text().strip()))
        except:
            pass

    return max(pages) if pages else 1


def extract_old_price(item):
    bdi = item.select_one("del span.woocommerce-Price-amount.amount bdi")
    return int(re.sub(r'\D', '', bdi.get_text())) if bdi else 0


def extract_new_price(item):
    bdi = item.select_one("ins span.woocommerce-Price-amount.amount bdi")
    return int(re.sub(r'\D', '', bdi.get_text())) if bdi else 0


def extract_en_title(item):
    title = item.select_one("p.name.product-title a").get_text(strip=True)
    return title.split("|")[1].strip() if "|" in title else ""


def extract_fa_title(item):
    title = item.select_one("p.name.product-title a").get_text(strip=True)
    return title.split("|")[0].strip()


def extract_photo_link(item):
    img = item.select_one("div.image-none img")
    return img.get("src") if img else ""


def extract_point(item):
    point = item.select_one("strong.rating")
    return float(point.text.strip()) if point else 0


def collect_data(site_address: str):
    site = requests.get(site_address)
    if not site:
        return []

    soup = BeautifulSoup(site.text, 'html.parser')
    div_collection = soup.find(
        'div',
        {'class': 'products row row-small large-columns-5 medium-columns-4 '
                  'small-columns-2 has-shadow row-box-shadow-2 '
                  'row-box-shadow-3-hover has-equal-box-heights equalize-box'}
    )

    if not div_collection:
        return []

    return div_collection.find_all('div', {'class': 'product-small box'})


def register_brands(brandname, brandlink):
    brands_col.update_one(
        {"brand_name": brandname},
        {"$set": {"brand_link": brandlink}},
        upsert=True
    )


def save_to_db(items, brandname):
    for item in items:
        master_col.update_one(
            {
                "brand": brandname,
                "english_name": extract_en_title(item)
            },
            {
                "$set": {
                    "name": extract_fa_title(item),
                    "point": extract_point(item),
                    "old_price": extract_old_price(item),
                    "new_price": extract_new_price(item),
                    "photo": extract_photo_link(item),
                }
            },
            upsert=True
        )


# -------------------------------
#   Main program
# -------------------------------
site = requests.get(web_url)
soup = BeautifulSoup(site.text, 'html.parser')
div_brand_collection = soup.find('div', {'class': 'row row-box-shadow-4-hover'})
div_brands = div_brand_collection.find_all('div', {'class': 'col-inner box-shadow-4'})
brand_collection_dict = {}

for item in div_brands:
    link = item.find('a', href=True)['href']
    if link == "#":
        continue

    link_site = requests.get(link)
    if not link_site:
        continue

    link_soup = BeautifulSoup(link_site.text, 'html.parser')
    product_block = link_soup.find(
        'div',
        {'class': 'products row row-small large-columns-5 medium-columns-4 '
                  'small-columns-2 has-shadow row-box-shadow-2 '
                  'row-box-shadow-3-hover has-equal-box-heights equalize-box'}
    )

    if product_block:
        brand = link.split("/")[-2]
        brand_collection_dict.setdefault(brand, link)

for brand_name, brand_link in brand_collection_dict.items():
    register_brands(brand_name, brand_link)

    for page in range(1, total_pages(brand_link) + 1):
        items = collect_data(f"{brand_link}page/{page}/")
        save_to_db(items, brand_name)
