from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain_community.document_loaders import WebBaseLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import time
import logging
import os
import sys
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # absolute location
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='log.log'
    )
logging.getLogger(__name__)

options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-unsafe-swiftshader")

model_name = f"{model_path}/sentiment-roberta-large-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def get_sentiment(link):
    try:
        loader = WebBaseLoader(link)
        docs = loader.load()
    except:
        return [None, None]
    text = [t.page_content for t in docs]
    text = ". ".join(text)
    try:
        inputs = tokenizer(text, return_tensors="pt", padding='max_length', truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            # predicted_class = torch.argmax(logits, dim=1).item()
            probabilities = F.softmax(logits, dim=1)
        return probabilities.tolist()[0]
    except Exception as e:
        print(f"Error: {e}")
        logging.info(f"Error: {e}")
        return [None, None]


def main(url):
    tag = True
    count = 0
    while tag:
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            tag = False
        except Exception as e :
            print(f"Error: {e}")
            driver.quit()
            count +=1
            if count < 10:
                time.sleep(1)
                continue
            else:
                return [None, None, None]
    try:
        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detail_pane"]/div[@class="post-header"]/h1/a[2]/span[@class="icon icon-link-external"]')))
    except Exception as e:
        logging.info(f"Error: {e}")
        logging.info("Browswer opened!")
        driver.quit()
        time.sleep(1)
        # options.arguments.remove("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        try:
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detail_pane"]/div[@class="post-header"]/h1/a[2]/span[@class="icon icon-link-external"]')))
            # options.add_argument("--headless")
        except:
            logging.info("Error: Element not found")
            driver.quit()
            # options.add_argument("--headless")
            return [None, None, None]
    try:
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
    except Exception as e:
        print(e)
        logging.info(e)
        return [None, None, None]
    tag = True
    count = 0
    while tag:
        try:
            WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
            tag = False
        except Exception as e:
            print(e)
            logging.info(e)
            count += 1
            if count > 10:
                return [current_url, None, None]
    driver.switch_to.window(driver.window_handles[-1])
    current_url = driver.current_url
    print(current_url)
    logging.info(f"{current_url}")
    driver.quit()
    sentiment = get_sentiment(current_url)
    print(sentiment)
    logging.info(f"{sentiment}")
    return current_url, sentiment[0], sentiment[1]
