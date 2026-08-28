import os
import getpass
import config
import requests
import platform
from urllib3 import encode_multipart_formdata
import session
import logging

logger = logging.getLogger(__name__)


class TradingviewAuthService:
  def __init__(self):
    print('Getting sessionid from db')
    self.sessionid = session.get_sessionid() or 'abcd'

    headers = {'cookie': 'sessionid=' + self.sessionid}
    test = requests.request("GET", config.urls["tvcoins"], headers=headers)
    print(test.text)
    print('sessionid in use: ' + str(self.sessionid))

    if test.status_code != 200:
      print('session id from db is invalid')
      username = os.environ.get('TV_USERNAME')
      if not username:
        username = input('TradingView username: ').strip()
        while not username:
          username = input('TradingView username: ').strip()

      password = os.environ.get('TV_PASSWORD')
      if not password:
        password = getpass.getpass('TradingView password: ')
        while not password:
          password = getpass.getpass('TradingView password: ')

      try:
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
        logger.info('TradingView login response: %s, %s',
                    login.status_code, (login.text or '')[:1000])
        sessionid = cookies.get('sessionid')
        if sessionid:
          self.sessionid = sessionid
          session.set_sessionid(self.sessionid)

      except Exception as e:
        logger.exception('Error performing login')
