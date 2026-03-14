import os
from flask import Flask, request, abort
from tradingview import tradingview
import json

app = Flask(__name__)


@app.route('/validate/<username>', methods=['GET'])
def validate(username):
  try:
    print(username)
    tv = tradingview()
    response = tv.validate_username(username)
    return json.dumps(response), 200, {
      'Content-Type': 'application/json; charset=utf-8'
    }
  except Exception as e:
    print("[X] Exception Occured : ", e)
    failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
    return json.dumps(failureResponse), 500, {
      'Content-Type': 'application/json; charset=utf-8'
    }

@app.route('/bulk_access', methods=['POST', 'DELETE'])
def bulk_access():
  try:
      jsonPayload = request.json
      pine_ids = jsonPayload.get('pine_ids')
      usernames = jsonPayload.get('usernames')
      print(jsonPayload)
      print(pine_ids)
      tv = tradingview()
      accessList = []
      for pine_id in pine_ids:
          for user in usernames:
              access = tv.get_access_details(user, pine_id)
              accessList.append(access)
      if request.method == 'POST':
          duration = '1L'
          dNumber = int(duration[:-1])
          dType = duration[-1:]
          for access in accessList:
              tv.add_access(access, dType, dNumber)

      if request.method == 'DELETE':
          for access in accessList:
              tv.remove_access(access)
      return json.dumps(accessList), 200, {
          'Content-Type': 'application/json; charset=utf-8'
      }
  except Exception as e:
      print("[X] Exception Occurred : ", e)
      failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
      return json.dumps(failureResponse), 500, {
          'Content-Type': 'application/json; charset=utf-8'
      }

@app.route('/access/<username>', methods=['POST', 'DELETE'])
def access(username):
  try:
    jsonPayload = request.json
    pine_ids = jsonPayload.get('pine_ids')

    tv = tradingview()
    validation_response = tv.validate_username(username)

    if not validation_response.get('validuser'):
      print("[X] Username doesn't exist")
      return json.dumps({'errorMessage': "Username doesn't exist"}), 404, {
        'Content-Type': 'application/json; charset=utf-8'
      }
    accessList = []
    for pine_id in pine_ids:
      access = tv.get_access_details(username, pine_id)
      accessList = accessList + [access]
    if request.method == 'POST':
      duration = '1L'
      dNumber = int(duration[:-1])
      dType = duration[-1:]
      for access in accessList:
        tv.add_access(access, dType, dNumber)

    if request.method == 'DELETE':
      for access in accessList:
        tv.remove_access(access)
    return json.dumps(accessList), 200, {
      'Content-Type': 'application/json; charset=utf-8'
    }

  except Exception as e:
    print("[X] Exception Occured : ", e)
    failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
    return json.dumps(failureResponse), 500, {
      'Content-Type': 'application/json; charset=utf-8'
    }


@app.route('/info/<username>', methods=['GET'])
def info(username):
  try:
    jsonPayload = request.json
    pine_ids = jsonPayload.get('pine_ids')
    print(jsonPayload)
    print(pine_ids)
    tv = tradingview()
    accessList = []
    for pine_id in pine_ids:
      access = tv.get_access_details(username, pine_id)
      accessList = accessList + [access]
    return json.dumps(accessList), 200, {
      'Content-Type': 'application/json; charset=utf-8'
    }

  except Exception as e:
    print("[X] Exception Occured : ", e)
    failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
    return json.dumps(failureResponse), 500, {
      'Content-Type': 'application/json; charset=utf-8'
    }


@app.route('/')
def main():
  return 'Your bot is alive!'


def start_server():
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
