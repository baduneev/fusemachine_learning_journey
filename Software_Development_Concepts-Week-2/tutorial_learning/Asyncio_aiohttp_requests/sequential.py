# requests library import gareko
# Yo HTTP request send garna use huncha, e.g. GET, POST, PUT, DELETE
import requests

# time module import gareko
# Yo execution time measure garna use huncha
import time


# URLs ko list banako
# Sabai URLs httpbin.org/delay/2 ho
# Yo endpoint le response dina 2 seconds delay garcha
urls = [
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/2",
]


# Program start hune time record gareko
start = time.time()


# urls list vitra ko each URL ma one-by-one request pathaune loop
for url in urls:

    # Current URL ma GET request send gareko
    # requests.get() synchronous/blocking huncha
    # Meaning: first request complete नभएसम्म next request start हुँदैन
    response = requests.get(url)

    # Response ko HTTP status code print gareko
    # 200 means request successful
    print(response.status_code)


# Program end hune time record gareko
end = time.time()


# Total execution time print gareko
# end - start le program run huna kati seconds lagyo calculate garcha
print("Total time:", end - start)