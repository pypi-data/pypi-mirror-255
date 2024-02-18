from base64 import b64encode, b64decode
from binascii import unhexlify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def enc_cbc(msg,password,iv):
    iv = unhexlify(iv)
    password = unhexlify(password)
    msg = pad(msg.encode(), AES.block_size)
    cipher = AES.new(password, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(msg)
    out = b64encode(cipher_text).decode('utf-8')
    return out

def dec_cbc(msg,password,iv):
    iv = unhexlify(iv)
    password = unhexlify(password)
    msg = pad(msg.encode(), AES.block_size)
    decipher = AES.new(password, AES.MODE_CBC, iv)
    plaintext = unpad(decipher.decrypt(b64decode(msg)), AES.block_size).decode('utf-8')
    return plaintext

def enc_ecb(msg,key,BLOCK_SIZE):
    cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    msg = cipher.encrypt(pad(msg.encode('utf8'), BLOCK_SIZE))
    return b64encode(msg).decode('utf-8')

def dec_ecb(msg,key,BLOCK_SIZE):
    msg = b64decode(msg)
    decipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    msg_dec = decipher.decrypt(msg)
    return unpad(msg_dec, BLOCK_SIZE)