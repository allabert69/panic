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
    count = 0
    for p in range(1, 100, 1):  
        print(f"page: {p}")
        logging.info(f"page: {p}")

        params = {
            "auth_token": os.environ.get("api_key"),
            "currencies": "BTC,BNB,Bitcoin,bitcoin",
            "kind": 'news',
            "page": p
        }
        count_panic = 0
        tag = True
        while tag:
            try:
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print(f"cryptopanic.com Error: {response.status_code} {response.reason}")
                    logging.info(f"cryptopanic.com Error: {response.status_code} {response.reason}")
                    time.sleep(1)
                    count_panic += 1  
                else:
                    tag = False                                                                            
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                logging.info(f"Request failed: {e}")
                print(response.json())
                logging.info(f"{response.json()}")
                count_panic += 1
            if count_panic > 10:
                break
        if count_panic > 10:
            print("cryptopanic.com Error: 10 times")
            logging.info("cryptopanic.com Error: 10 times")
            break
        else: 
            data = response.json()
            results = data['results']
            df = pd.DataFrame(results)

            with sqlite3.connect(db_file) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM articles where sent_1 IS NOT NULL")
                idx = cur.fetchall()
                idx = [i[0] for i in idx]

            df = df[~df['id'].isin(idx)].reset_index(drop=True)
            df = df.dropna(subset="url").reset_index(drop=True)
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
                df = df.dropna(subset="sent_1").reset_index(drop=True)
                if not df.empty:
                    with sqlite3.connect(db_file) as conn:
                        df.to_sql('articles', con=conn, if_exists='append', index=False)
            else:
                count += 1
                print(f"zero count: {count}")
                logging.info(f"zero count: {count}")
                if count < 10:
                    continue
                else:
                    break
    logging.info(f"job success!: {datetime.now()}")
    logging.info("---------------------------")
    print(f"job success!: {datetime.now()}")
    print("---------------------------")


# schedule.every().day.at("03:05").do(job)
# schedule.every().day.at("06:05").do(job)
# schedule.every().day.at("09:05").do(job)
# schedule.every().day.at("12:05").do(job)
# schedule.every().day.at("15:05").do(job)
# schedule.every().day.at("18:05").do(job)
# schedule.every().day.at("21:05").do(job)
# schedule.every().day.at("00:05").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(300)

job()