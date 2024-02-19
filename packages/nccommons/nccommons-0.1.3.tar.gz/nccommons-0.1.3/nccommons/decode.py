import base64

def decode_base64(encoded_text):
    decoded_bytes = base64.b64decode(encoded_text)
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text