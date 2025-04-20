import pandas as pd
import requests
import os
import sqlite3
import schedule
import time
from datetime import datetime
import logging
import dotenv
dotenv.load_dotenv()
import get_link
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # absolute location

db_file = "panic.db"
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='log.log'
    )
logging.getLogger(__name__)

url = f"https://cryptopanic.com/api/v1/posts/"


def job():
    print(f"job started: {datetime.now()}")
    logging.info(f"job started: {datetime.now()}")
    for p in range(1, 200, 1):
        print(f"page: {p}")
        logging.info(f"page: {p}")
        params = {
            "auth_token": os.environ.get("api_key"),
            "currencies": "BTC,BNB,Bitcoin,bitcoin",
            "kind": 'news',
            "page": p
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"cryptopanic.com Error: {response.status_code}")
            logging.info(f"cryptopanic.com Error: {response.status_code}")
            break
        else:
            data = response.json()
            results = data['results']
            df = pd.DataFrame(results)

            with sqlite3.connect(db_file) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM articles")
                idx = cur.fetchall()
                idx = [i[0] for i in idx]

            df = df[~df['id'].isin(idx)]
            print(f"cryptopanic shape: {df.shape}")
            logging.info(f"cryptopanic shape: {df.shape}")
            if not df.empty:
                df = df.drop(["source", "votes"], axis=1)
                df["published_at"] = pd.to_datetime(df["published_at"])
                df["created_at"] = pd.to_datetime(df["created_at"])
                df["currencies"] = df["currencies"].apply(lambda x: x[0]["code"])

                cols = df.columns.tolist()
                for i, v in enumerate(["id", "created_at", "published_at"]):
                    el = cols.pop(cols.index(v))
                    cols.insert(i, el)
                df = df.reindex(columns=cols)

                df[["link", "sent_0", "sent_1"]] = df.apply(lambda x: get_link.main(x["url"]), axis=1, result_type="expand")
                with sqlite3.connect(db_file) as conn:
                    df.to_sql('articles', con=conn, if_exists='append', index=False)
            else:
                break
    logging.info(f"job succecc!: {datetime.now()}")


schedule.every().day.at("03:05").do(job)
schedule.every().day.at("06:05").do(job)
schedule.every().day.at("09:05").do(job)
schedule.every().day.at("12:05").do(job)
schedule.every().day.at("15:05").do(job)
schedule.every().day.at("18:05").do(job)
schedule.every().day.at("21:05").do(job)
schedule.every().day.at("00:05").do(job)

while True:
    schedule.run_pending()
    time.sleep(300)

# job()