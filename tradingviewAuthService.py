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
        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'

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
        logger.debug('Login response cookies: %s', cookies)

        sessionid = cookies.get('sessionid')
        if sessionid:
          self.sessionid = sessionid
          session.set_sessionid(self.sessionid)
        else:
          logger.error('Error with the login session: %s, %s',
                    login.status_code, (login.text or '')[:1000])
          raise Exception('Internal Server Error')

      except Exception as e:
        logger.exception('Error performing login')
        raise Exception('Internal Server Error')
