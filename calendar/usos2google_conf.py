"""USOS2google configuration. If in trouble, see http://winemore.w.staszic.waw.pl/usos2google.html"""
import pytz

# USOS necessary configuration
usosapi_base_url = 'http://apps.usos.edu.pl/'; # url to usos api, default UW
consumer_key = 'insert_here';
consumer_secret = 'insert_here';
# USOS optional configuration
access_token_key = 'insert_here_if_you_want'
access_token_secret = 'insert_here_if_you_want'
# Timezone configuration
mytz=pytz.timezone('Europe/Warsaw')
# You may use this dict to provide nicer names for courses, for -s option.
#names_dict={
# "1000-111bAM1b" : "Analiza I.1 (p II)",
# "1000-211bPM" : "Podst. Mat",
# "1000-211bWPF" : "WPF",
# }
