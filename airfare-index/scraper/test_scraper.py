import requests
from bs4 import BeautifulSoup

url = "https://example.com"

response = requests.get(url)

print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

print("Page title:", soup.title.text)
print("Heading:", soup.h1.text)