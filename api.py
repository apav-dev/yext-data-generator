import requests
import json
import os
from dotenv import load_dotenv


ReviewSubmission = {
    "entity": {
        "id": str
    },
    "authorName": str,
    "authorEmail": str,
    "title": str,
    "rating": int,
    "content": str,
    "status": str,
    "date": str
}

load_dotenv()


def submit_review(review):
    api_key = os.getenv("REVIEW_SUBMISSION_API_KEY")
    if api_key is None:
        print("API key not found. Please set the environment variable.")
        return

    url = f"https://liveapi.yext.com/v2/accounts/me/reviewSubmission?api_key={api_key}&v=20221113"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(review))
        if response.status_code != 202:
            print(f"Error submitting review: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(e)


def get_product_data(page_token=None, product_type=None):
    api_key = os.getenv("CONTENT_API_KEY")
    if api_key is None:
        print("API key not found. Please set the environment variable.")
        return

    url = f'https://cdn.yextapis.com/v2/accounts/me/content/skis?api_key={api_key}&v=20230601'
    # if page_token, append pageToken to url
    if page_token:
        url = url + f"&pageToken={page_token}"
    if product_type:
        url = url + f"&c_categoryName={product_type}"
    response = requests.get(url)

    # You can process the response data as per your requirement
    data = response.json()

    return data


def get_locations(page_token=None):
    api_key = os.getenv("CONTENT_API_KEY")
    if api_key is None:
        print("API key not found. Please set the environment variable.")
        return

    url = f'https://cdn.yextapis.com/v2/accounts/me/content/locations?api_key={api_key}&v=20230601'
    # if page_token, append pageToken to url
    if page_token:
        url = url + f"&pageToken={page_token}"
    response = requests.get(url)

    # You can process the response data as per your requirement
    data = response.json()

    return data
