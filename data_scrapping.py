from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import io
import pandas as pd

# Configure Edge options
edge_options = Options()
edge_options.add_argument("--ignore-certificate-errors")

# Specify the correct path to EdgeDriver
edge_service = Service(r"C:\edgedriver\msedgedriver.exe")

# Initialize Edge WebDriver
driver = webdriver.Edge(service=edge_service, options=edge_options)
driver.get("https://aqicn.org/station/@482590/")

# Print page title for debugging
print("Page Title:", driver.title)

# Update the assertion if necessary
assert "Air Pollution" in driver.title  # Adjust this based on the actual title


def scroll_down(driver, increment=500, max_attempts=10):
    for i in range(max_attempts):
        driver.execute_script("window.scrollBy(0, arguments[0]);", increment)
        time.sleep(3)
        try:
            element = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[6]/div[1]/div[2]/center[4]/div[3]/div/center[2]/div[2]",
                    )
                )
            )
            return element
        except:
            continue
    return None


try:
    # Scroll down the page in increments until the element is found
    element = scroll_down(driver)

    if element:
        # Ensure the element is in view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(2)  # Wait for scrolling to complete

        # Click the button using JavaScript
        driver.execute_script("arguments[0].click();", element)
        print("Button clicked successfully.")

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[1])

        # Wait for the page to load completely
        time.sleep(5)

        # Print page title for debugging
        print("New Tab Page Title:", driver.title)

        # Extract the CSV data from the body
        try:
            # Extract text from the body of the new tab
            csv_data = driver.find_element(By.TAG_NAME, "body").text

            # Print raw CSV data for debugging
            print("Raw CSV Data:\n", csv_data)

            # Convert the text data into a file-like object
            csv_file = io.StringIO(csv_data)

            # Try reading the CSV data with handling for bad lines
            try:
                df = pd.read_csv(
                    csv_file, delimiter=",", skiprows=4, on_bad_lines="warn"
                )
                print("DataFrame Head:\n", df.head())

                print(len(df))
                file_path = "./sample_data.csv"
                df.columns = [
                    "date",
                    "min",
                    "max",
                    "median",
                    "q1",
                    "q3",
                    "stdev",
                    "count",
                ]
                df.to_csv(file_path, index=False)
            except pd.errors.ParserError as e:
                print(f"Parsing error: {e}")
        except Exception as e:
            print(f"An error occurred while extracting CSV data: {e}")

    else:
        print("Element not found after scrolling.")
except Exception as e:
    print(f"An error occurred: {e}")

# Close the driver
driver.quit()
