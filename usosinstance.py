# import settings
#
# CONSUMER_KEY = 'consumer_key'
# CONSUMER_SECRET = 'consumer_secret'
# CONSUMER_NAME = 'name'
# CONSUMER_URL = 'url'
#
#
# class UsosInstance:
#     name = None
#     url = None
#     consumer_key = None
#     consumer_secret = None
#
#     def __init__(self, usos_id, name, url, consumer_key, consumer_secret):
#         self.osos_id = usos_id
#         self.name = name
#         self.url = url
#         self.consumer_key = consumer_key
#         self.consumer_secret = consumer_secret
#
#
# class UsosInstances:
#     usoses = {}
#
#     def __init__(self):
#         for key in settings.USOSINSTANCES.keys():
#             poz = settings.USOSINSTANCES[key]
#             self.usoses[key] = UsosInstance(key, poz[CONSUMER_NAME], poz[CONSUMER_URL], poz[CONSUMER_KEY], poz[CONSUMER_SECRET])
#
#     def getbyid(self, name):
#         for k in self.usoses:
#             if k == name:
#                 return self.usoses[k]
#         return None
#
