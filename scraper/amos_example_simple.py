from playwright.sync_api import sync_playwright
import time 

# pip install pytest-playwright
# playwright install
def run(playwright):


    browser = playwright.chromium.launch(
        headless=False,
        
        )
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Navigate to google.com
    page.goto("https://www.google.com/")

    # Click on the button with text "abctext"
    # button = page.get_by_role("button", name="abctext")
    # if button:
    #     button.click()
    # else:
    #     print("Button with text 'abctext' not found.")

    # click on element with text "edf"
    page.click("text=Alle ablehnen")

    # click on element with id "myid"
    page.click("#myid")

    # sleep 5 seconds
    page.wait_for_timeout(5000)

    # get all images with class "myclass"
    images = page.query_selector_all(".myclass")

    # get src
    for image in images:
        print(image.get_attribute("src"))

    # Close the browser
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)