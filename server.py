import os
from flask import Flask, request, make_response
import logging
from tradingview import tradingview
import json
#from threading import Thread
app = Flask('')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def require_api_key():
  api_key = os.environ.get('apiKey')
  provided = request.headers.get('Api-Key')
  if provided != api_key:
    logger.warning('Invalid API key provided: %s', provided)
    return make_response(json.dumps({'errorMessage': 'Not Found'}), 404)
  return None


@app.route('/validate/<username>', methods=['GET'])
def validate(username):
  try:
    # abort if api key is not valid
    error = require_api_key()
    if error:
      return error

    logger.info('Validate request for username: %s', username)    
    tv = tradingview()
    response = tv.validate_username(username)
    return json.dumps(response), 200, {
      'Content-Type': 'application/json; charset=utf-8'
    }
  except Exception as e:
    logger.exception('Exception in validate: %s', e)
    resp = make_response(json.dumps({'errorMessage': 'Unknown Exception Occurred'}), 500)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/access/<username>', methods=['GET', 'POST', 'DELETE'])
def access(username):
  try:
    # abort if api key is not valid
    error = require_api_key()
    if error:
      return error

    jsonPayload = request.json
    pine_ids = jsonPayload.get('pine_ids')
    print(jsonPayload)
    print(pine_ids)
    tv = tradingview()
    accessList = []
    for pine_id in pine_ids:
      access = tv.get_access_details(username, pine_id)
      accessList = accessList + [access]

    if request.method == 'POST':
      duration = jsonPayload.get('duration')
      dNumber = int(duration[:-1])
      dType = duration[-1:]
      for access in accessList:
        tv.add_access(access, dType, dNumber)

    if request.method == 'DELETE':
      for access in accessList:
        tv.remove_access(access)
    resp = make_response(json.dumps(accessList), 200)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp

  except Exception as e:
    logger.exception('Exception in access: %s', e)
    resp = make_response(json.dumps({'errorMessage': 'Unknown Exception Occurred'}), 500)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp



@app.route('/')
def main():
  return 'Your bot is alive!'


# def run():
#   app.run(host='0.0.0.0', port=5000)

# def start_server_async():
#   server = Thread(target=run)
#   server.start()


def start_server():
  app.run(host='0.0.0.0', port=5000)
