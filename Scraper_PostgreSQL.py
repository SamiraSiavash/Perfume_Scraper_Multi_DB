import requests
from bs4 import BeautifulSoup
import psycopg2
import re

# -------------------------------
#   PostgreSQL
# -------------------------------
web_url = "https://liliome.com/%D8%A8%D8%B1%D9%86%D8%AF%D9%87%D8%A7-%D8%B9%D8%B7%D8%B1-%D8%A7%D8%AF%DA%A9%D9%84%D9%86-%D9%81%D8%B1%D9%88%D8%B4%DA%AF%D8%A7%D9%87-%D8%B9%D8%B7%D8%B1-%D9%84%DB%8C%D9%84%DB%8C%D9%88%D9%85"
database = "Perfume"
connection_string = f"dbname={database} user=postgres password=123456 host=localhost port=5432"

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
            num = int(li.get_text().strip())
            pages.append(num)
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
    title_tag = item.select_one("p.name.product-title a")
    title = title_tag.get_text(strip=True)
    return title.split("|")[1].strip() if "|" in title else ""


def extract_fa_title(item):
    title_tag = item.select_one("p.name.product-title a")
    title = title_tag.get_text(strip=True)
    return title.split("|")[0].strip()


def extract_photo_link(item):
    img_tag = item.select_one("div.image-none img")
    return img_tag.get("src") if img_tag else ""


def extract_point(item):
    point_tag = item.select_one("strong.rating")
    return float(point_tag.text.strip()) if point_tag else 0


def collect_data(site_address: str):
    site = requests.get(site_address)
    if not site:
        print("The page could not be loaded!")
        return

    soup = BeautifulSoup(site.text, 'html.parser')
    div_collection = soup.find(
        'div',
        {'class': 'products row row-small large-columns-5 medium-columns-4 '
                  'small-columns-2 has-shadow row-box-shadow-2 '
                  'row-box-shadow-3-hover has-equal-box-heights equalize-box'}
    )

    if not div_collection:
        print("No products found!")
        return

    items = div_collection.find_all('div', {'class': 'product-small box'})
    return items


def save_to_db(items, brandname, con):
    if not items:
        return

    cur = con.cursor()
    for item in items:
        cur.execute(
            "INSERT INTO Master(Brand,EnglishName,Name,Point,OldPrice,NewPrice,Photo) "
            "VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (
                brandname,
                extract_en_title(item),
                extract_fa_title(item),
                extract_point(item),
                extract_old_price(item),
                extract_new_price(item),
                extract_photo_link(item),
            )
        )


def create_tables():
    try:
        with psycopg2.connect(connection_string) as con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS Master CASCADE;")
            cur.execute("DROP TABLE IF EXISTS Brands CASCADE;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Brands (
                        Brand_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        Brand_Link TEXT NOT NULL,
                        Brand_Name TEXT
                    );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Master (
                    ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    Brand TEXT NOT NULL,
                    EnglishName TEXT NOT NULL,
                    Name TEXT NOT NULL,
                    Point FLOAT NOT NULL,
                    OldPrice INT NOT NULL,
                    NewPrice INT NOT NULL,
                    Photo TEXT NOT NULL
                );
            """)
    except Exception as ex:
        print(ex)


def register_brands(brandname: str, brandlink: str, con):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO Brands(Brand_Name,Brand_Link) VALUES(%s,%s)",
        (brandname, brandlink),
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

create_tables()

with psycopg2.connect(connection_string) as con:
    con.autocommit = True
    for brand_name, brand_link in brand_collection_dict.items():
        register_brands(brand_name, brand_link, con)

        pages = total_pages(brand_link)
        for i in range(1, pages + 1):
            items = collect_data(f"{brand_link}page/{i}/")
            save_to_db(items, brand_name, con)
