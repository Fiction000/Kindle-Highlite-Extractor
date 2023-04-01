import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Replace these with your Amazon email and password
email = AMAZON_EMAIL
password = AMAZON_PASSWORD

# Initialize the WebDriver (change the path if necessary)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Navigate to the Kindle Notebook page and log in. Chnge the URL if you're not using a Japanese Amazon account.
driver.get("https://read.amazon.co.jp/kp/notebook/") 
email_input = driver.find_element(by=By.NAME, value='email')
email_input.send_keys(email)
password_input = driver.find_element(by=By.NAME, value='password')
password_input.send_keys(password)
password_input.send_keys(Keys.RETURN)

# Wait for the page to load
time.sleep(5)

# Get the list of books
books = driver.find_elements(by=By.CSS_SELECTOR, value=".kp-notebook-library-each-book")


with open("kindle_annotations.md", "w", encoding="utf-8") as f:
    # Iterate through books and scrape annotations
    for i, book in enumerate(books):
        # Retry the book click operation in case of a StaleElementReferenceException
        while True:
            try:
                book.click()
                time.sleep(3)
                break
            except:
                books = driver.find_elements(by=By.CSS_SELECTOR, value=".kp-notebook-library-each-book")
                book = books[i]

        # Get book details
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.find("h3", class_="a-spacing-top-small a-color-base kp-notebook-selectable kp-notebook-metadata").text.strip()
        author = soup.find("p", class_="a-spacing-none a-spacing-top-micro a-size-base a-color-secondary kp-notebook-selectable kp-notebook-metadata").text.strip()
        f.write(f"# Title: {title}\n")
        f.write(f"## Author: {author}\n\n")

        # Get annotations
        annotations = soup.find_all("div", class_="a-row a-spacing-base")
        for i, annotation in enumerate(annotations, 1):
            highlight = annotation.find("span", class_="a-size-base-plus a-color-base")
            note = annotation.find("span", id="note")
            
            if highlight:
                f.write(f"### Annotation {i} - Highlight:\n")
                f.write(f"{highlight.text.strip()}\n\n")
            if note and note.text.strip():
                f.write(f"### Annotation {i} - Note:\n")
                f.write(f"{note.text.strip()}\n\n")

        # Go back to the list of books
        time.sleep(3)

# Close the WebDriver
driver.quit()
