import requests
import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def get_outfit_images(query: str, per_page=3):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return [photo["src"]["medium"] for photo in data.get("photos", [])]
