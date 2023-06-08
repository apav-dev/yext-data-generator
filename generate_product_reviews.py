import datetime
from api import submit_review, get_product_data
import json
import openai
import os
from dotenv import load_dotenv
import concurrent.futures


openai.api_key = os.getenv("OPEN_AI_API_KEY")


def format_prompt(average_rating, product_name, oldest_date, product_type="pair of skis"):
    return f"""
  generate json that includes the following fields:
    - authorName  
    - authorEmail
    - title
    - rating
    - content
    - reviewDate

  authorName should be the name of a character from famous tv shows and be in the form of a first name and last initial
  authorEmail should be associated with the authorName
  rating should be between 1 and 5. The average of all the ratings should equal {average_rating}.
  content should be a short review of a {product_type} called {product_name} and be associated with the rating. For example, if the rating is a 3, the review would say something like "These skis are ok but I have some issues with them"
  title should be a short title for the review and should be associated with the content. For example, if the content is "These skis are ok but I have some issues with them", the title could be "Ok but has some issues"
  reviewDate should be in the form yyyy-mm-dd and should be between {oldest_date} and {datetime.date.today()}

  Return a list of 10 JSON objects and nothing else.
"""


def generate_reviews(average_rating, product_name, oldest_date, product_type):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=format_prompt(average_rating, product_name,
                             oldest_date, product_type),
        max_tokens=2048,
        temperature=0.9,
    )

    try:
        data = json.loads(response.choices[0].text)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")


def get_all_products():
    products = []
    page_token = None

    while True:
        data = get_product_data(page_token=page_token, product_type="Skis")
        response = data.get('response')
        for product in response.get('docs', []):
            product_id = product.get('id')
            product_name = product.get('name')
            product_type = product.get('c_categoryName')
            if product_id:
                products.append([product_id, product_name, product_type])

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return products


def process_product(product):
    product_type_map = {
        "Skis": "pair of skis",
        "Ski Boot": "pair of ski boots",
        "Binding": "pair of ski bindings",
        "Poles": "pair of ski poles",
    }
    product_id, product_name, product_type = product

    print(f"Generating reviews for {product_name} - {product_type}...")
    reviews = generate_reviews(
        4.5, product_name, "2022-10-01", product_type_map[product_type])
    for review in reviews:
        review["entity"] = {"id": product_id}
        review["status"] = "LIVE"
    for review in reviews:
        submit_review(review)

    print(
        f"Submitted {len(reviews)} reviews for {product_name} - {product_type}")


def main():
    products = get_all_products()
    print(f"Found {len(products)} products")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_product, products)


if __name__ == "__main__":
    main()
