import requests
from bs4 import BeautifulSoup

url = "https://example.com"

response = requests.get(url)

print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

title = soup.title

print("Page title:", title.text)