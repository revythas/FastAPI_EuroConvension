import json
import os
import sys
from datetime import datetime, timedelta
from datetime import timedelta
from datetime import date
from pydantic import BaseModel
from typing import Optional

import httpx
import redis
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

class Item(BaseModel):
    price: float
    currency: str
    date : Optional[str] = None


# curl -X GET "http://localhost:5000/route-optima/USD" -H  "accept: application/json"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":213.2,\"currency\":\"USD\"}"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":100,\"currency\":\"USD\"}"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":150.38,\"currency\":\"NZD\"}"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":150.38,\"currency\":\"NZD\"}"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":130,\"currency\":\"CAD\"}"

# testing
# curl -X POST "httpc_date=2015-2-2" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":100,\"currency\":\"USD\"}"
# curl -X POST "http://localhost:5000/currency/" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"price\":100,\"currency\":\"USD\"}"

def seconds_until_midnight():
    """ Get the number of seconds until midnight """
    tomorrow = datetime.now() + timedelta(1)
    midnight = datetime(year=tomorrow.year, month=tomorrow.month, 
                        day=tomorrow.day, hour=0, minute=0, second=0)
    return (midnight - datetime.now()).seconds


def connect_to_redis() -> Optional[redis.Redis]:
    try:
        client = redis.Redis(
            host=os.environ.get("HOST"),
            port=int(os.environ.get("REDIS_PORT")),
            password=os.environ.get("REDIS_PASSWORD"),
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("Authentication Error")
        sys.exit(1)


client = connect_to_redis()


def get_currency(item) -> dict:
    with httpx.Client() as client:
        if item.date is not None:
            base_url = "https://api.exchangeratesapi.io/{}".format(item.date)
        else:
            base_url = "https://api.exchangeratesapi.io/latest"
        url = "{}?base=EUR".format(base_url)
        response = client.get(url)
        print(url)
        return response.json()

def get_values_from_cache(key: str) -> str:
    """ Retrive data from redis """
    print("Get with key : {}".format(key))
    val = client.get(key)
    return val


def set_values_to_cache(key: str, value: str) -> bool:
    """ Save data to redis """

    # Assume that we have caching period of until the midnight
    state = client.setex(key, timedelta(seconds=seconds_until_midnight()), value=value,)
    return state


def calculate_currency(item: Item, ) -> dict:
    """ Calculate the current currency retrieving each time the value from API or from cache """

    converted_currency = {}
    if item.currency == "EUR":
        converted_currency["price_in_euro"] = item.price
        return converted_currency
    
    # First it looks for the data in redis cache
    concat_key = item.currency + "-" + str(item.date)
    data = get_values_from_cache(key=concat_key)

    # If cache is found then serves the data from cache
    if data is not None:
        print("Serve data from cache")
        data = json.loads(data)
        converted_currency["price_in_euro"] = item.price / data
        return converted_currency

    else:
        # If cache is not found then sends request to the API
        print("Serve data from API")
        data = get_currency(item)
        
        # This block sets saves the respose to redis and serves it directly
        if data.get("rates"):
            for i in data["rates"]:
                concat_key = str(i) + "-" + str(item.date)
                state = set_values_to_cache(key=concat_key, value=data["rates"][i])
            if state is True:
                converted_currency["price_in_euro"] = item.price / data.get("rates").get(item.currency)
            return converted_currency


app = FastAPI()


@app.post("/currency/")
async def view(item: Item, historic_date: Optional[str] = None):
    if historic_date is not None:
        item.date = str(historic_date)
    else:
        today = date.today()
        item.date = today.strftime("%Y-%m-%d")
    return calculate_currency(item)
