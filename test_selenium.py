import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Try different URLs based on environment
        app_url = os.getenv('APP_URL', 'http://localhost:3000')
        self.driver.get(app_url)
        self.driver.implicitly_wait(10)
        
        # Wait for page to load
        self.wait = WebDriverWait(self.driver, 10)

    def test_1_add_task(self):
        driver = self.driver
        try:
            # Wait for the input field to be present
            input_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "itemInput"))
            )
            input_box.clear()
            input_box.send_keys("Test Task")
            
            submit_btn = driver.find_element(By.CSS_SELECTOR, "form#itemForm button")
            submit_btn.click()
            time.sleep(2)

            # Wait for the task to appear in the list
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul#itemsList li"))
            )
            self.assertTrue(any("Test Task" in item.text for item in items), "Task not found after addition")
            print("✅ Add task test passed")
        except Exception as e:
            print(f"❌ Add task test failed: {str(e)}")
            self.driver.save_screenshot("/tmp/add_task_failure.png")
            raise

    def test_2_toggle_task_completion(self):
        driver = self.driver
        try:
            # Add a task first
            input_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "itemInput"))
            )
            input_box.clear()
            input_box.send_keys("Toggle Task")
            driver.find_element(By.CSS_SELECTOR, "form#itemForm button").click()
            time.sleep(2)

            # Find and click the toggle button
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul#itemsList li"))
            )
            if items:
                toggle_button = items[0].find_element(By.CLASS_NAME, "toggle-btn")
                toggle_button.click()
                time.sleep(2)

                # Check if task is marked as completed
                updated_item = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")[0]
                name_span = updated_item.find_element(By.CSS_SELECTOR, ".item-content span")
                self.assertIn("completed", name_span.get_attribute("class"), "Task not marked completed")
                print("✅ Toggle task completion test passed")
        except Exception as e:
            print(f"❌ Toggle task completion test failed: {str(e)}")
            self.driver.save_screenshot("/tmp/toggle_task_failure.png")
            raise

    def test_3_delete_task(self):
        driver = self.driver
        try:
            # Add a task first
            input_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "itemInput"))
            )
            input_box.clear()
            input_box.send_keys("Delete Task")
            driver.find_element(By.CSS_SELECTOR, "form#itemForm button").click()
            time.sleep(2)

            # Get initial count of items
            initial_items = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")
            initial_count = len(initial_items)

            if initial_items:
                # Find and click the delete button
                delete_button = initial_items[0].find_element(By.CLASS_NAME, "delete-btn")
                delete_button.click()
                time.sleep(2)

                # Check if task is deleted
                items_after = driver.find_elements(By.CSS_SELECTOR, "ul#itemsList li")
                final_count = len(items_after)
                
                self.assertTrue(final_count < initial_count or 
                              all("Delete Task" not in item.text for item in items_after), 
                              "Task not deleted")
                print("✅ Delete task test passed")
        except Exception as e:
            print(f"❌ Delete task test failed: {str(e)}")
            self.driver.save_screenshot("/tmp/delete_task_failure.png")
            raise

    def tearDown(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    print("🚀 Starting Selenium tests for Task Manager...")
    unittest.main(verbosity=2)
