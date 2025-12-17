# 🌸 Perfume Scraper

A Python-based web scraping project designed to extract structured perfume product data from **Liliome.com**.  
The scraper collects brand and product information and supports **multiple database backends**, allowing the same data pipeline to be stored in **relational and NoSQL databases**.

---

## 📌 Features

### ✔ Robust HTTP session  
- Uses `requests.Session` with retry logic  
- Handles connection failures gracefully (`safe_get()`)

### ✔ Web scraping  
- **Extracts**:
  - **Brand name**
  - **English title**
  - **Persian title**
  - **Old price**
  - **New price**
  - **Product rating (Point)**
  - **Photo URL**
- Automatically discovers all available brands and their product pages

### ✔ Pagination handling  
- Detects number of pages for each brand using `total_pages()`

---

## 🗄️ Supported Databases

The project has been refactored to support **multiple storage backends**, making it easy to switch between databases:

- **SQLite** – lightweight local storage
- **SQL Server** – enterprise relational database
- **PostgreSQL** – open-source relational database
- **MongoDB** – NoSQL document-based storage

This design enables comparison between **SQL and NoSQL data models** using the same scraping logic.
Two tables are created automatically:

#### `Brands`
| Column       | Type    | Description |
|--------------|---------|-------------|
| Brand_ID     | INTEGER | Primary key |
| Brand_Link   | TEXT    | URL of brand page |
| Brand_Name   | TEXT    | Extracted brand name |

#### `Master`
| Column       | Type    | Description |
|--------------|---------|-------------|
| ID           | INTEGER | Primary key |
| Brand        | TEXT    | Brand slug |
| EnglishName  | TEXT    | Product English title |
| Name         | TEXT    | Product Persian title |
| Point        | FLOAT   | Product rating |
| OldPrice     | INTEGER | Old price |
| NewPrice     | INTEGER | New price |
| Photo        | TEXT    | Image URL |

---

## 🛠 Technologies Used

- **Python 3**
- **Requests**
- **BeautifulSoup4**
- **SQLite3**
- **SQL Server**
- **PostgreSQL**
- **MongoDB**
- **Retry & Timeout handling**
- **Regex for price cleanup**

---

## 📁 Project Structure

```
Perfume_Scraper/
│
├── assets/
│ └── mongodb_brands.png
│ └── mongodb_master.png
│ └── postgres_brands.png
│ └── postgres_master.png
│ └── sqlite_brands.png
│ └── sqlite_master.png
│ └── sqlserver_brands.png
│ └── sqlserver_master.png
│
├── db/
│ └── Perfume.db # Automatically created database for SQLite
│
├── Scraper_MongoDB.py
├── Scraper_MongoDB_Safe.py
├── Scraper_PostgreSQL.py
├── Scraper_PostgreSQL_Safe.py
├── Scraper_SQL.py
├── Scraper_SQL_Safe.py
├── Scraper_SQLite.py
├── Scraper_SQLite_Safe.py
├── README.md
├── requirements.txt
```

---

## 🚀 How It Works

### 1️⃣ Load Liliome brand list  
The script visits:


https://liliome.com/برندها-عطر-ادکلن-فروشگاه-عطر-لیلیوم


It finds all brand links and stores them in the `Brands` table.

---

### 2️⃣ For each brand:  
- Detects how many pages of products exist  
- Extracts products from each page  
- Saves structured data into the `Master` table

---

## 🖼 Screenshots
### SQLite
```markdown
![Brands Table](assets/sqlite_brands.png)
```
<img width="950" height="536" alt="sqlite_brands" src="https://github.com/user-attachments/assets/005cf739-cdc3-4d7e-8631-bb43372f728e" />

```markdown
![Master Table](assets/sqlite_master.png)
```
<img width="1160" height="665" alt="sqlite_master" src="https://github.com/user-attachments/assets/95172bd3-033c-4686-af87-a3de1a8c0440" />

---

### SQL Server
```markdown
![Brands Table](assets/sqlserver_brands.png)
```
<img width="967" height="535" alt="sqlserver_brands" src="https://github.com/user-attachments/assets/56d2e13a-8098-4e0b-a4d1-cac76c815c51" />

```markdown
![Master Table](assets/sqlserver_master.png)
```
<img width="1060" height="592" alt="sqlserver_master" src="https://github.com/user-attachments/assets/b62f96c0-2a48-443d-8cdd-981bc85bed45" />

---

### PostgreSQL
```markdown
![Brands Table](assets/postgres_brands.png)
```
<img width="917" height="562" alt="postgres_brands" src="https://github.com/user-attachments/assets/b792a284-6804-486a-b0ad-7a28606d2184" />

```markdown
![Master Table](assets/postgres_master.png)
```
<img width="1138" height="598" alt="postgres_master" src="https://github.com/user-attachments/assets/0d5d0075-53c1-4b88-b6f6-11b2d8118bab" />

---

### MongoDB
```markdown
![Brands Collection](assets/mongodb_brands.png)
```
<img width="1308" height="592" alt="mongodb_brands" src="https://github.com/user-attachments/assets/69a99e3b-5900-49d1-bc12-b20f8e2ad35a" />

```markdown
![Master Collection](assets/mongodb_master.png)
```
<img width="1564" height="733" alt="mongodb_master" src="https://github.com/user-attachments/assets/c016ecd5-0cef-488b-9f7b-c542e0d167cb" />

---

## 📝 Notes

* Adjust CSS selectors depending on website structure.
* Website layouts may change; update selectors accordingly.
* Always follow the target website’s Terms of Service.

---

## 📄 License
MIT License (optional)

---

## ✨ Author
**Samira Siavash**

🔗 GitHub: [https://github.com/SamiraSiavash](https://github.com/SamiraSiavash)

🔗 LinkedIn: [https://linkedin.com/in/samira-siavash](https://linkedin.com/in/samira-siavash)
