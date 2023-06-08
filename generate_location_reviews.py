import datetime
from api import get_locations, submit_review
import json
import openai
import os
from dotenv import load_dotenv
import concurrent.futures


openai.api_key = os.getenv("OPEN_AI_API_KEY")


def format_prompt(average_rating, location_city, oldest_date):
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
  content should be a short review of a ski shop in {location_city} and be associated with the rating. For example, if the rating is a 5, the review would say something like "The selection is great and the staff is very helpful"
  title should be a short title for the review and should be associated with the content. For example, if the content is "The selection is great and the staff is very helpful", the title could be "Amazing selection and helpful staff"
  reviewDate should be in the form yyyy-mm-dd and should be between {oldest_date} and {datetime.date.today()}

  Return a list of 10 JSON objects and nothing else.
"""


def generate_reviews(average_rating, location_city, oldest_date):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=format_prompt(average_rating, location_city,
                             oldest_date),
        max_tokens=2048,
        temperature=0.9,
    )

    try:
        data = json.loads(response.choices[0].text)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")


def get_all_locations():
    locations = []
    page_token = None

    while True:
        data = get_locations(page_token)
        response = data.get('response')
        for location in response.get('docs', []):
            location_id = location.get('id')
            location_name = location.get('name')
            location_address = location.get('address')
            if location_id:
                locations.append(
                    [location_id, location_name, location_address])

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return locations


def process_location(location):
    location_id, location_name, location_address = location

    print(
        f"Generating reviews for {location_name} - {location_address['city']}...")
    reviews = generate_reviews(
        4.5, location_address['city'], "2022-10-01")
    for review in reviews:
        review["entity"] = {"id": location_id}
        review["status"] = "LIVE"
    for review in reviews:
        submit_review(review)

    print(
        f"Submitted {len(reviews)} reviews for {location_name} - {location['city']}")


def main():
    locations = get_all_locations()
    print(f"Found {len(locations)} locations")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_location, locations)


if __name__ == "__main__":
    main()
