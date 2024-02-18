import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError, ExpiredSignatureError


def validate_jwt(encoded_jwt):
	try:
		return 200, jwt.decode(encoded_jwt, 'quasi_utils_as_a_key', algorithms='HS256')
	except InvalidSignatureError as e:
		return 401, str(e)
	except DecodeError as e:
		return 403, str(e)
	except ExpiredSignatureError as e:
		return 406, str(e)
