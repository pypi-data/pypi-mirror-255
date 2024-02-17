from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

def encrypt_aes(key, message):
    """
    The function encrypts a message using the AES encryption algorithm with a given key.
    
    :param key: The key parameter is the encryption key used to encrypt the message. It should be a byte
    string of length 16, 24, or 32, corresponding to AES-128, AES-192, or AES-256 encryption
    respectively
    :param message: The `message` parameter is the plaintext message that you want to encrypt. It should
    be a string
    :return: the encrypted password, which includes the nonce, ciphertext, and tag.
    """
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
    return nonce + ciphertext + tag

def decrypt_aes(key, ciphertext):
    """
    The function `decryptPassword` takes a key and a ciphertext as input, decrypts the ciphertext using
    AES encryption, and returns the plaintext password if the decryption is successful, otherwise it
    returns None.
    
    :param key: The key parameter is the encryption key used to encrypt the plaintext. It should be a
    byte string of length 16, 24, or 32, corresponding to AES-128, AES-192, or AES-256 encryption
    respectively
    :param ciphertext: The `ciphertext` parameter is the encrypted message that needs to be decrypted.
    It is a byte string that contains the encrypted data
    :return: the decrypted plaintext as a string if the decryption is successful. If the decryption
    fails, it returns None.
    """
    nonce = ciphertext[:16]
    tag = ciphertext[-16:]
    ciphertext = ciphertext[16:-16]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        return plaintext.decode('utf-8')
    except ValueError:
        return None

def compute_key(secret, salt, length = 32):
    """
    The function `compute_key` takes a secret, salt, and optional length as input, and returns a key
    computed using the PBKDF2 algorithm with SHA512 as the HMAC hash module.
    
    :param secret: The secret is the password or passphrase that you want to use to generate the key. It
    should be a string
    :param salt: The salt is a random value that is added to the secret before hashing. It is used to
    add an extra layer of security and prevent precomputed attacks. The salt should be unique for each
    secret and should be stored securely along with the hashed key
    :param length: The length parameter specifies the desired length of the key in bytes. By default, it
    is set to 32 bytes, defaults to 32 (optional)
    :return: the key generated using the PBKDF2 algorithm with the given secret, salt, and length.
    """
    password = secret.encode()
    key = PBKDF2(password, salt, length, count=1000000, hmac_hash_module=SHA512)
    return key

def encrypt(secret, message, algorithm = 'AES', length = 256):
    """
    The function encrypts a message using a specified algorithm and key length, and returns the
    algorithm, key length, salt, and encrypted text.
    
    :param secret: The secret is a string that is used as the input to compute the encryption key. It is
    a secret value that should be known only to the sender and receiver of the encrypted message
    :param message: The `message` parameter is the text or data that you want to encrypt
    :param algorithm: The algorithm parameter specifies the encryption algorithm to be used. In this
    case, the only supported algorithm is 'AES', which stands for Advanced Encryption Standard, defaults
    to aes (optional)
    :param length: The "length" parameter specifies the length of the encryption key in bits. It can be
    either 256, 192, or 128, defaults to 256 (optional)
    :return: a tuple containing the algorithm used for encryption, the length of the encryption key, the
    salt used for encryption, and the encrypted text.
    """
    salt = get_random_bytes(16)

    if length == 256:
        key = compute_key(secret, salt)
    elif length == 192:
        key = compute_key(secret, salt, 24)
    elif length == 128:
        key = compute_key(secret, salt, 16)
    else:
        print(str(length) + ' is not supported as length')
        return None

    if algorithm == 'AES':
        encrypted_text = encrypt_aes(key, message)
    else:
        print(algorithm + ' is not supported as algorithm')
        return None

    return (algorithm, length, salt, encrypted_text)

def decrypt(secret, ciphertext, salt, algorithm = 'AES', length = 256):
    """
    The function decrypts a ciphertext using a secret key and specified encryption algorithm and key
    length.
    
    :param secret: The secret is a string that is used as the input to compute the encryption key. It is
    typically a password or a passphrase
    :param ciphertext: The ciphertext is the encrypted text that you want to decrypt. It is the output
    of the encryption process
    :param salt: The salt is a random value that is used as an additional input to the key derivation
    function. It adds randomness to the process of generating the encryption key, making it more secure
    :param algorithm: The algorithm parameter specifies the encryption algorithm to be used for
    decryption. In this case, the only supported algorithm is 'AES', which stands for Advanced
    Encryption Standard, defaults to aes (optional)
    :param length: The length parameter specifies the length of the encryption key to be used. It can
    have three possible values: 256, 192, or 128. These values correspond to the key lengths of 256
    bits, 192 bits, and 128 bits respectively, defaults to 256 (optional)
    :return: the decrypted text.
    """
    if length == 256:
        key = compute_key(secret, salt)
    elif length == 192:
        key = compute_key(secret, salt, 24)
    elif length == 128:
        key = compute_key(secret, salt, 16)
    else:
        print(str(length) + ' is not supported as length')
        return None

    if algorithm == 'AES':
        decrypted_text = decrypt_aes(key, ciphertext)
    else:
        print(algorithm + ' is not supported as algorithm')
        return None

    return decrypted_text
