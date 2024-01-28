import requests
from bs4 import BeautifulSoup
import re
import csv


# What are u looking for ?
LOOKING_FOR = "iphone"
MY_POSTAL_CODE = 94901 #81101
RADIUS = 30
PAGES_TO_EXPLORE = 14
POSTS_SHOWING = 0


all_links = []
def get_links():
    global POSTS_SHOWING, all_links

    for page in range(PAGES_TO_EXPLORE):
        URL = f"https://www.bazos.sk/search.php?hledat={LOOKING_FOR}&hlokalita={MY_POSTAL_CODE}&humkreis={RADIUS}&cenaod=&cenado=&order=&crz={POSTS_SHOWING}"

        # Request
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")

        # Get links
        posts = soup.find_all("div", class_="inzeraty inzeratyflex")
        for post in posts:
            link = post.find("a")
            link = link.get("href")
            all_links.append(link)

        # Next page
        POSTS_SHOWING += 20

def standardize_model_name(model):
    # Regular expression to identify 'iPhone'
    model_regex = r"(iPhone)\s*(\d+)(\s*(Pro\s*Max|Pro|Mini|Plus)?)"

    # Function to insert a space between 'iPhone' and the number if missing
    def insert_space(match):
        model_part = match.group(1)  # 'iPhone'
        number_part = match.group(2)  # Model number like '12'
        type_part = match.group(3).strip()  # Model type like 'Pro Max', 'Pro', etc.
        return f"{model_part} {number_part} {type_part}".strip()

    # Apply the function to standardize the model name
    standardized_model = re.sub(model_regex, insert_space, model, flags=re.IGNORECASE)
    return standardized_model

def get_data():
    # CSV file setup
    csv_file = "iPhone_data.csv"

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Model", "Memory Size", "Battery Health", "Price", "Link"])
        writer.writeheader()

        for link in all_links:
            r = requests.get(link)
            soup = BeautifulSoup(r.text, "html.parser")

            title = soup.find("h1", class_="nadpisdetail").get_text(strip=True)
            description = soup.find("div", class_="popisdetail").get_text(strip=True)
            container = soup.find(class_="listadvlevo")
            b_tags = container.find_all('b')
            price = b_tags[1].get_text(strip=True)

            data = (title + "\n" + description + "\n" + price).lower()

            # Regular expressions for extracting specific details
            model_regex = r"iPhone\s*\d+\s*(Pro\s*Max|Pro|Mini|Plus)?"
            memory_regex = r"(\d+)\s*GB"
            battery_regex = r"(\d+)%"

            # Extract iPhone model
            model_match = re.search(model_regex, data, re.IGNORECASE)
            if model_match:
                model = model_match.group(0)
                model = standardize_model_name(model)
            else:
                model = "Model not found"

            # Extract memory size
            memory_match = re.search(memory_regex, data, re.IGNORECASE)
            memory_size = memory_match.group(0) if memory_match else "Memory size not found"

            # Extract battery health
            battery_match = re.search(battery_regex, data)
            battery_health = battery_match.group(0) if battery_match else "Battery health not found"


            # Data to write
            data_to_write = {
                "Model": model,
                "Memory Size": memory_size,
                "Battery Health": battery_health,
                "Price": price,
                "Link": link
            }
            writer.writerow(data_to_write)
            print("Writing...")

        print("Done")


get_links()
get_data()

