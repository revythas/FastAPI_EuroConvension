import requests
import json
import httpx

DATE_TO_TEST = "2015-2-2"

# We test the rest functionality and validity. We check USD price in euro for a 
# specific historical date.

def test_post_headers_body_json():
    url = "http://localhost:5000/currency/?historic_date={}".format(DATE_TO_TEST)
    
    # Additional headers.
    headers = {"Content-Type": "application/json" }

    # Body
    payload = {"currency": "USD", "price": 100}

    # convert dict to json string by json.dumps() for body data. 
    resp = requests.post(url, headers=headers, data=json.dumps(payload, indent=4))       
    
    # Validate status --> should be 200
    assert resp.status_code == 200
    resp_body = resp.json()

    # Validate response
    assert resp_body == {"price_in_euro": 88.41732979664015}
