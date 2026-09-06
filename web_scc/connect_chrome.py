from playwright.sync_api import sync_playwright
import json


API_URL_PART = "/v2/flight/search"


with sync_playwright() as p:

    print("Connecting to Chrome...")

    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    print("Connected successfully.")

    context = browser.contexts[0]

    page = context.new_page()

    print("Opening IndiGo...")

    page.goto(
        "https://www.goindigo.in/flights",
        wait_until="domcontentloaded"
    )

    print("IndiGo opened.")
    print()
    print("Now perform the search manually in the browser:")
    print()
    print("From: Delhi (DEL)")
    print("To: Kolkata (CCU)")
    print("Date: 20 September 2026")
    print("Trip: One Way")
    print("Passengers: 1")
    print()
    print("The program will automatically detect the API response.")
    print("DO NOT press Enter.")
    print()


    def handle_response(response):

        if API_URL_PART in response.url:

            print()
            print("===================================")
            print("SEARCH API RESPONSE DETECTED")
            print("===================================")

            print("URL:")
            print(response.url)

            print()
            print("STATUS:")
            print(response.status)

            try:

                data = response.json()

                print()
                print("JSON RESPONSE RECEIVED")

                print()
                print("Top-level keys:")
                print(list(data.keys()))

                with open(
                    "search_response.json",
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        data,
                        file,
                        indent=4
                    )

                print()
                print("Saved as:")
                print("search_response.json")

                print()
                print("SUCCESS!")

            except Exception as error:

                print()
                print("Could not read JSON response:")
                print(error)


    page.on(
        "response",
        handle_response
    )


    # Keep the program alive while you perform the search.
    try:

        while True:
            page.wait_for_timeout(1000)

    except KeyboardInterrupt:

        print()
        print("Stopped.")

        browser.close()