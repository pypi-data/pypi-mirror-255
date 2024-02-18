from json_repair import repair_json
import jwt

def decode_cae_url(cae_jwt, strip_whitespace=True, attempt_to_repair_json=False):

    decoded_jwt = bytes.decode(jwt.utils.base64url_decode(cae_jwt))

    if attempt_to_repair_json:
        decoded_jwt = repair_json(decoded_jwt)

    if strip_whitespace:
        decoded_jwt = decoded_jwt.replace(' ','').replace('\r', '').replace('\n','').replace('\t', '')

    return decoded_jwt