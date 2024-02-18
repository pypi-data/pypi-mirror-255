import re

class ApiKeyValidator:
    INVALID_API_KEY_MESSAGE = "Invalid or missing API key (sign up at covalenthq.com/platform)"
    _apiKeyV1Pattern = re.compile(r"^ckey_([a-f0-9]{27})$")
    _apiKeyV2Pattern = re.compile(r"^cqt_(wF|rQ)([bcdfghjkmpqrtvwxyBCDFGHJKMPQRTVWXY346789]{26})$")

    def __init__(self, apiKey):
        self._apiKey = apiKey

    def is_valid_api_key(self):
        return self._apiKeyV1Pattern.match(self._apiKey) or self._apiKeyV2Pattern.match(self._apiKey)
