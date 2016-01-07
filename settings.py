VERSION = 001
PORT = 8888

DATE_FORMAT = "%d-%m-%y"
DEFAULT_SCHEDULE_PERIOD = 7

MONGODB_URI = "mongodb://dbuser1:dbpass1@ds035995.mongolab.com:35995/usos-test2"


user = "Luk" # lub "Luk" lub "Woj"
if user == "Woj":
    #OUTH for USOS
    # Consumer Key to use.
    consumer_key = 'KBt6uWPWUekUzFtNTyY9'
    consumer_secret = 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG'
    # USOS API Base URL, trailing slash included.
    usosapi_base_url = 'https://usosapps.uw.edu.pl/'

    # You may want to hardcode these values, so you won't need to reauthorize ***
    access_token_key = '3ShYQv8LyvgeXthKJzmJ'
    access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
else:
    consumer_key = 'equujDB5ZLzTmPfcy2c2'
    consumer_secret = 'PNMLtvWr6p34tmYSjmDKfNwQEmUdkMwExearQhWA'
    usosapi_base_url = 'https://api.usos.tu.kielce.pl/'

    # You may want to hardcode these values, so you won't need to reauthorize ***
    access_token_key = 'uXLyCGpp5zfHPH4z4brg'
    access_token_secret = 'VLd6AGJL574qpPNfJyKJ2NR7mxh9VEQJKZYtwaRy'

