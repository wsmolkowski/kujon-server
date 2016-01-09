
class User:
    name = None
    user_id = None
    usos_id = None
    access_token_key = None
    access_token_secret = None

    def __init__(self, user_id, usos_id, access_token_key, access_token_secret):
        self.user_id = user_id
        self.usos_id = usos_id
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

# class Contacts(json.JSONEncoder):
#     contacts = {}
#     name = ""
#
#
# class User:
#     def __init__(self,user_id,access_token_key, access_token_secret):
#
#         if not self.ifexists(user_id):
#             self.register(user_id,access_token_key,access_token_secret)
#
#
#     def ifexists(self):
#         #sprawdzenie czy user istnieje
#         return True
#
#     def register(self):
#         return True
#
#     def updateuserdata(self):
#         return True


'''
def create_user( user_id, usos_id, access_token_key, access_token_secret):
    return {
            id_mobile = user_id
            access_token_key = '3ShYQv8LyvgeXthKJzmJ'
            access_token_secret = 'JwSUygmyJ85Pp3g9LfJsDnk48MkfYWQzg7Chhd7Y'
            usus_id = 'UW'
        }

class Usos:
    name = None
'''

