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
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # absolute location

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

model_name = f"{root_path}/sentiment-roberta-large-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def geet_sentiment(link):
    loader = WebBaseLoader(link)
    docs = loader.load()
    text = [t.page_content for t in docs]
    text = ". ".join(text)

    inputs = tokenizer(text, return_tensors="pt", padding='max_length', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        # predicted_class = torch.argmax(logits, dim=1).item()
        probabilities = F.softmax(logits, dim=1)
    return probabilities.tolist()[0]


def main(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detail_pane"]/div[@class="post-header"]/h1/a[2]/span[@class="icon icon-link-external"]')))
    except:
        driver.quit()
        time.sleep(1)
        options.arguments.remove("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="detail_pane"]/div[@class="post-header"]/h1/a[2]/span[@class="icon icon-link-external"]')))
        options.add_argument("--headless")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()
    WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(3))
    driver.switch_to.window(driver.window_handles[-1])
    current_url = driver.current_url
    print(current_url)
    driver.quit()
    sentiment = geet_sentiment(current_url)
    print(sentiment)
    return current_url, sentiment[0], sentiment[1]



