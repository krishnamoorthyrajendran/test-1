import jwt
import uuid
from datetime import datetime, timedelta,timezone
from dateutil.relativedelta import *


class JWT_:

  def __init__(self, secret, user_id="" ):

        self.secret = secret
        self.user_id = user_id


  def get_access_token(self):

        try:
            set_time = datetime.now(timezone.utc) + timedelta(hours=24)

            payload = {
                        "user": self.user_id,
                        'exp': set_time,
                        'key': "access_token"
                        }

            encode_token = jwt.encode( payload, self.secret, algorithm='HS256')
            # print("Access token is created ..............",encode_token)
            return ("true",str(encode_token),str(set_time))

        except Exception as dd:
            # print("Error in token generation ...............",str(dd))
            return ("false","somthing went wrong")

  def validate_access_token(self, access_token):

        try:
            decode_token = jwt.decode(access_token, self.secret, algorithms=['HS256'])
            # print("Token is still valid and active")
            return ("true","valid-token",decode_token)
        except jwt.ExpiredSignatureError:
            # print("Token expired. Get new one")
            return ("false","token-expired","")
        except jwt.InvalidTokenError:
            # print("Invalid Token")
            return ("false","invalid-token","")

  def get_refresh_token(self):

        try:
            payload = {
                        "user": self.user_id,
                        'exp': datetime.now() + timedelta(hours=24),
                        'key': "refresh_token"
                        }
            encode_token = jwt.encode( payload, self.secret, algorithm='HS256')
            # print("Refresh token is created ..............",encode_token)
            return ("true",str(encode_token))

        except:
            # print("Error in token generation ...............")
            return ("false","somthing went wrong")


  def validate_refresh_token(self,refresh_token):

        try:
            decode_token = jwt.decode(refresh_token, self.secret, algorithms=['HS256'])
            # print("Token is still valid and active")
            return ("true","valid_token",decode_token)
        except jwt.ExpiredSignatureError:
            # print("Token expired. Get new one")
            return ("false","token_expired","")
        except jwt.InvalidTokenError:
            # print("Invalid Token")
            return ("false","invalid_token","")

