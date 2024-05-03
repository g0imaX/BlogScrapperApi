from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/posts', methods=['GET'])
def get_posts():
    # Get the URL from the request parameters
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400

    # Check if URL has a scheme (protocol) specified
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        # Prepend 'http://' as default protocol if missing
        url = 'http://' + url

    # Send a request to the website
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch URL'}), response.status_code

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract post titles
    post_titles = [title.text for title in soup.find_all('h3', class_='post-title')]

    # Extract post dates and strip newline characters
    post_dates = [date.find('time').text.strip() for date in soup.find_all('a', class_='timestamp-link')]

    # Extract post details
    post_details_div = soup.find('div', class_='snippet-item r-snippetized')
    if post_details_div:
        post_details = post_details_div.text.strip()
    else:
        post_details = "Post details not found."

    # Extract image URLs
    thumbnail_divs = soup.find_all('div', class_='snippet-thumbnail')
    image_urls = [thumbnail_div.find('img')['src'] for thumbnail_div in thumbnail_divs]

    # Create JSON response
    response_data = {
        'posts': [{
            'title': title,
            'date': date,
            'details': post_details,
            'image_url': image_url
        } for title, date, image_url in zip(post_titles, post_dates, image_urls)]
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
