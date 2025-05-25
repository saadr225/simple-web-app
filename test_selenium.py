import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class TaskManagerTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver.get("http://localhost:3000")
        self.driver.get("http://host.docker.internal:3000")
        self.driver.implicitly_wait(5)

    def test_1_add_task(self):
        driver = self.driver
        input_box = driver.find_element(By.ID, "itemInput")
        input_box.send_keys("Test Task")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "form#itemForm button")
        submit_btn.click()
        time.sleep(1)

        items = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")
        self.assertTrue(any("Test Task" in item.text for item in items), "Task not found after addition")

    def test_2_toggle_task_completion(self):
        driver = self.driver
        input_box = driver.find_element(By.ID, "itemInput")
        input_box.send_keys("Toggle Task")
        driver.find_element(By.CSS_SELECTOR, "form#itemForm button").click()
        time.sleep(1)

        item = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")[0]
        toggle_button = item.find_element(By.CLASS_NAME, "toggle-btn")
        toggle_button.click()
        time.sleep(1)

        updated_item = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")[0]
        name_span = updated_item.find_element(By.CSS_SELECTOR, ".item-content span")
        self.assertIn("completed", name_span.get_attribute("class"), "Task not marked completed")

    def test_3_delete_task(self):
        driver = self.driver
        input_box = driver.find_element(By.ID, "itemInput")
        input_box.send_keys("Delete Task")
        driver.find_element(By.CSS_SELECTOR, "form#itemForm button").click()
        time.sleep(1)

        item = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")[0]
        delete_button = item.find_element(By.CLASS_NAME, "delete-btn")
        delete_button.click()
        time.sleep(1)

        items_after = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")
        self.assertTrue(all("Delete Task" not in item.text for item in items_after), "Task not deleted")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
