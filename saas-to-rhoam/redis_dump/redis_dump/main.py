import json
import logging
import os
import time
from pathlib import Path

import redis

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


def get_string_value(r: redis.Redis, key):
    return r.get(key)


def get_set_value(r: redis.Redis, key):
    return list(r.smembers(key))


def get_hash_value(r: redis.Redis, key):
    return r.hgetall(key)


def get_unknown(r, key):
    return "unknown"


get_values = {
    "string": get_string_value,
    "set": get_set_value,
    "hash": get_hash_value,
}


def put_string_value(r: redis.Redis, key, value: str):
    return r.set(key, value)


def put_set_value(r: redis.Redis, key, value: list):
    return r.sadd(key, set(value))


def put_hash_value(r: redis.Redis, key, value: dict):
    return r.hset(key, value, "")


def put_unknown(r, key):
    return "unknown"


put_values = {
    "string": put_string_value,
    "set": put_set_value,
    "hash": put_hash_value,
}


def pull():
    start = time.time()
    logging.info("pulling metric data")

    r = redis.Redis(host=os.environ['URI'], port=int(os.environ['PORT']), decode_responses=True)
    keys = []

    accounts = os.environ['ACCOUNTS']
    accounts = accounts.split(',')
    match = []
    for account in accounts:
        match += [
            f"service_id:{account}/",
            f"service:{account}/",
            f"service/id:{account}/",
        ]

    total_keys = r.dbsize()
    cursor = None
    mark = 0
    count = 1000
    divider = round(total_keys/count/20)
    percent = 0
    logging.info("starting key scan")
    logging.info(f"keys to scan: {total_keys:,}")
    while cursor is None or cursor != 0:
        if cursor is None:
            cursor = 0
        result = r.scan(cursor=cursor, count=count)
        cursor = result[0]
        val = [i for e in match for i in result[1] if e in i]
        keys += val

        if mark % divider == 0:
            logging.info(f"keys scanned: {percent}%")
            percent += 5
        mark += 1

    logging.info(f"keys collected: {len(keys):,}")

    all_data = []
    logging.info("getting key data")
    pipeline_size = 1000
    pipe = r.pipeline()
    percent_five = round(len(keys) / 20)
    percent_counter = 0

    local_keys = []
    for index, key in enumerate(keys):
        local_keys.append(key)
        if len(local_keys) == pipeline_size:
            for local_key in local_keys:
                pipe.type(local_key)
            types = pipe.execute()

            for item in zip(local_keys, types):
                get_values.get(item[1], get_unknown)(pipe, item[0])
            values = pipe.execute()

            for item in zip(local_keys, types, values):
                all_data.append({'key': item[0], 'type': item[1], 'value': item[2]})
            local_keys.clear()

        if index % percent_five == 0:
            logging.info(f"data collected: {percent_counter}%")
            percent_counter += 5

    logging.info("key data collected")
    logging.info(f"total data points: {len(all_data):,}")

    logging.info("creating dump file")
    with open("data.json", "w") as df:
        json.dump(all_data, df, indent=2)

    logging.info("file: data.json created")

    logging.info(f"time taken: {round(time.time() - start, 2)} seconds")
    logging.info("Complete")


def push():
    logging.info("pushing resources")
    logging.info("look at the seed function for example of how to uploads the data.")


def seed():
    start = time.time()
    logging.info("seeding redis data")

    file_path = os.environ['file']
    target = os.environ['target']

    fp = Path(file_path)
    if not fp.is_file():
        logging.error("seed file not found")
        exit(1)

    with open(fp) as f:
        data = json.loads(f.read())

    rounds = round(int(target)/len(data))
    r = redis.Redis(host=os.environ['URI'], port=int(os.environ['PORT']), decode_responses=True)

    counter = 0
    percent_counter = 0
    pipe = r.pipeline()
    for i in range(rounds):
        for item in data:
            key = f"{item['key']}/{i}"
            value = item['value']
            put_values[item['type']](pipe, key, value)
            counter += 1
        pipe.execute()

        if i % round(rounds/20) == 0:
            logging.info(f"{percent_counter}% completed")
            percent_counter += 5

    logging.info(f"entries added: {counter:,}")
    logging.info(f"time taken: {round(time.time() - start, 2)} seconds")
    logging.info("complete")
