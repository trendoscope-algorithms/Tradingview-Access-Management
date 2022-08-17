from dateutil import parser
from dateutil.relativedelta import relativedelta
def get_access_extension(currentExpirationDate:str, extension_type:str, extension_length:int):
  expiration = parser.parse(currentExpirationDate)
  if(extension_type=='Y'):
    expiration = expiration + relativedelta(years=extension_length)
  elif(extension_type=='M'):
    expiration = expiration + relativedelta(months=extension_length)
  elif(extension_type=='W'):
    expiration = expiration + relativedelta(weeks=extension_length)
  elif(extension_type=='D'):
    expiration = expiration + relativedelta(days=extension_length)
  return str(expiration)