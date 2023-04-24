from rest_framework import status
from rest_framework.exceptions import APIException


class MessageTypeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ('You cannot add a media file to a text message. '
                      'If you want to send a message using a media file, '
                      'first delete the text message and create a new message with the media file.')
    default_code = 'invalid'


class UniqueError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There is already such a record in the database'
    default_code = 'invalid'


class TokenError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid token'
    default_code = 'invalid'


class AccountTypeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid account type'
    default_code = 'invalid'
