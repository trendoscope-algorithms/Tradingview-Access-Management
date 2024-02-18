import os
from replit import db
import config
import requests
import platform
from urllib3 import encode_multipart_formdata
from datetime import datetime, timezone
import helper


class tradingview:
  def __init__(self):
    print('Getting sessionid and sessionid_sign from db')
    self.sessionid = db["sessionid"] if 'sessionid' in db.keys() else 'abcd'
    self.sessionid_sign = db["sessionid_sign"] if 'sessionid_sign' in db.keys() else 'efgh'

    headers = {
      'cookie': f'sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}'
    }
    test = requests.request("GET", config.urls["tvcoins"], headers=headers)
    print(test.text)
    print('sessionid from db : ' + self.sessionid)
    if test.status_code != 200:
      print('session id or sessionid_sign from db is invalid')
      username = os.environ['tvusername']
      password = os.environ['tvpassword']

      payload = {'username': username, 'password': password, 'remember': 'on'}
      body, contentType = encode_multipart_formdata(payload)
      userAgent = 'TWAPI/3.0 (' + platform.system() + '; ' + platform.version(
      ) + '; ' + platform.release() + ')'
      print(userAgent)
      login_headers = {
        'origin': 'https://www.tradingview.com',
        'User-Agent': userAgent,
        'Content-Type': contentType,
        'referer': 'https://www.tradingview.com'
      }
      login = requests.post(config.urls["signin"],
                            data=body,
                            headers=login_headers)
      cookies = login.cookies.get_dict()
      self.sessionid = cookies["sessionid"]
      self.sessionid_sign = cookies["sessionid_sign"]
      db["sessionid"] = self.sessionid
      db["sessionid_sign"] = self.sessionid_sign

  def validate_username(self, username):
    users = requests.get(config.urls["username_hint"] + "?s=" + username)
    usersList = users.json()
    validUser = False
    verifiedUserName = ''
    for user in usersList:
      if user['username'].lower() == username.lower():
        validUser = True
        verifiedUserName = user['username']
    return {"validuser": validUser, "verifiedUserName": verifiedUserName}

  def get_access_details(self, username, pine_id):
    user_payload = {'pine_id': pine_id, 'username': username}

    user_headers = {
      'origin': 'https://www.tradingview.com',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': f'sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}'
    }
    print(user_payload)
    usersResponse = requests.post(config.urls['list_users'] +
                                  '?limit=10&order_by=-created',
                                  headers=user_headers,
                                  data=user_payload)
    userResponseJson = usersResponse.json()
    print(userResponseJson)
    users = userResponseJson['results']

    access_details = user_payload
    hasAccess = False
    noExpiration = False
    expiration = str(datetime.now(timezone.utc))
    for user in users:
      if user['username'].lower() == username.lower():
        hasAccess = True
        strExpiration = user.get("expiration")
        if strExpiration is not None:
          expiration = user['expiration']
        else:
          noExpiration = True

    access_details['hasAccess'] = hasAccess
    access_details['noExpiration'] = noExpiration
    access_details['currentExpiration'] = expiration
    return access_details

  def add_access(self, access_details, extension_type, extension_length):
    noExpiration = access_details['noExpiration']
    access_details['expiration'] = access_details['currentExpiration']
    access_details['status'] = 'Not Applied'
    if not noExpiration:
      payload = {
        'pine_id': access_details['pine_id'],
        'username_recip': access_details['username']
      }
      if extension_type != 'L':
        expiration = helper.get_access_extension(
          access_details['currentExpiration'], extension_type,
          extension_length)
        payload['expiration'] = expiration
        access_details['expiration'] = expiration
      else:
        access_details['noExpiration'] = True
      enpoint_type = 'modify_access' if access_details[
        'hasAccess'] else 'add_access'

      body, contentType = encode_multipart_formdata(payload)

      headers = {
        'origin': 'https://www.tradingview.com',
        'Content-Type': contentType,
        'Cookie': f'sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}'
      }
      add_access_response = requests.post(config.urls[enpoint_type],
                                          data=body,
                                          headers=headers)
      access_details['status'] = 'Success' if (
        add_access_response.status_code == 200
        or add_access_response.status_code == 201) else 'Failure'
    return access_details

  def remove_access(self, access_details):
    payload = {
      'pine_id': access_details['pine_id'],
      'username_recip': access_details['username']
    }
    body, contentType = encode_multipart_formdata(payload)

    headers = {
      'origin': 'https://www.tradingview.com',
      'Content-Type': contentType,
      'Cookie': f'sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}'
    }
    remove_access_response = requests.post(config.urls['remove_access'],
                                           data=body,
                                           headers=headers)
    access_details['status'] = 'Success' if (remove_access_response.status_code
                                             == 200) else 'Failure'
