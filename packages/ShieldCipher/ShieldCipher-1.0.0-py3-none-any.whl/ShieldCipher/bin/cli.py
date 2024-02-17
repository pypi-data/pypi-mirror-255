import sys
from ShieldCipher.encryption.symmetric import encrypt as sc_encrypt, decrypt as sc_decrypt
from getpass import getpass
import binascii

def msc():
    print("                     .                    .                           ")
    print("                :-:--=:-:::.             :=-**##*=:                   ")
    print("                 :=----------.         .-%@@@@@@@@@%:                 ")
    print("                :-------------:        :@@@@@@@@@@@@%.                ")
    print("               :-=-----------==:       +@@@@@@@@@@@@@#                ")
    print("              :=-=-------===-=--      .+%@@@@@@@@@@@#=                ")
    print("             .------------=------.     =@@@@@@@@@@@@@#                ")
    print("               --=--------==-=-.       -*%@@@@@@@@@*-.                ")
    print("                  ::----===+-             .#%@@@@*.                   ")
    print("                     -+++=: .               :+##+                     ")
    print("                    -+=====.              .=%@@%%%#=                  ")
    print("                 :-----------:.        :+#%%%@@@@@%@%+-               ")
    print("               -----------------      -%%%%%@@@%@@%%@%%*              ")
    print("              .-==----------==--:     #%%%@%@@@@@@@@@@%%.             ")
    print("              :-=+----------*=---    =%%%@@%%@@@%%@@@%%%=             ")
    print("              ---=----------*----:  .#%%%@@%%@@@%@%@@%%%%             ")
    print("             :-===----------+=---=  -#%%%@@%%@%@%@%@@%%%%=            ")
    print("               --=----------=#==+.   ==+%@@%%@@@%@%@@*++.             ")
    print("               --=-----------*=---  :===#@@%%@@@%@%%%--=              ")
    print("               -==-----------++--=  ---:#@%@@@%%%@@@%--=              ")
    print("               -=------------=:--=. =-- %@%%%%%%@%%%@=-=              ")
    print("              .-+-------------.:---.--: %%%%%%%%@%%@@+==              ")
    print("              :-++*++++++*+***. --=+--  *###########**-=              ")
    print("              --*+++++++++*+++: :--*-: :------=------*-=              ")
    print("              =-*++++++++*+***- .--*-. :-------------+-=              ")
    print("             .--*+++=+*++*+***+ :==*=: -------=------===:             ")
    print("             :=+++++==+++*++**+ -*++=. -------+-------+=:             ")
    print("              -++++=+==**+++***  :-:   -------+-------+.              ")
    print("               -+++=++=****+**#        -------+=------=               ")
    print("               .++==*=---=*+**+        =------+*------=               ")
    print("                ----=    :---=          ====-.::+====                 ")
    print("           :**#==---=:   ----= ..   .:::=--=+*%#*--=+***. .--:..      ")
    print("           .=+**#=--==   :=--=%@*:.-=+%%*--=: ::+=--+***+=#@%*-=-::.  ")
    print("               :+=--=. :::=--=:.-*#%*--=*---+-+**=--=--=+**+*=**%@%=  ")
    print("                 =--= .#%%=--=.  +*#%#= +---#%++#=---.+%@%+  .+++*+-  ")
    print("                 ====   .:+===:   -==+= :===*+: -==== .--:.      ..   ")
    print("                 =--=     ----:         .----   :=---                 ")
    print("                 ----     :---:         .=---   .=---                 ")
    print("                 ----     :---:         .=---    =---                 ")
    print("                 ---:     :---:         .=---    +---                 ")
    print("                 +##%.    =*##-         -%%#:    %%%#                 ")
    print("                :@@@@-    #@@@+         %@@@*   :@@@%:                ")
    print("                .====.    -++=:         =+==-    --==.                ")
    print("\n@milosnowcat\n")

def encrypt(args):
    """
    The `encrypt` function takes in a text and optional encryption options, encrypts the text using the
    ShieldCipher algorithm, and returns the encrypted text along with the algorithm, length, salt, and
    message.
    
    :param args: The `args` parameter is a list of command line arguments passed to the `encrypt`
    function
    :return: The function `encrypt` returns a string that represents the encrypted text.
    """
    if not args:
        msc()
        return "Usage: ShieldCipher encrypt \"text\" <options>"
        
    secret = getpass()

    algorithm = None
    length = None
    
    if "-a" in args:
        algorithm = args[args.index("-a") + 1]
    elif "--algorithm" in args:
        algorithm = args[args.index("--algorithm") + 1]

    if "-l" in args:
        length = args[args.index("-l") + 1]
    elif "--length" in args:
        length = args[args.index("--length") + 1]

    if algorithm and length:
        encrypted_text = sc_encrypt(secret, args[0], algorithm, int(length))
    elif algorithm:
        encrypted_text = sc_encrypt(secret, args[0], algorithm)
    elif length:
        encrypted_text = sc_encrypt(secret, args[0], length=int(length))
    else:
        encrypted_text = sc_encrypt(secret, args[0])

    encrypted_text_algorithm = encrypted_text[0]
    encrypted_text_length = str(encrypted_text[1])
    encrypted_text_salt = binascii.hexlify(encrypted_text[2]).decode('utf-8')
    encrypted_text_msg = binascii.hexlify(encrypted_text[3]).decode('utf-8')

    return encrypted_text_algorithm + '$' + encrypted_text_length + '$' + encrypted_text_salt + '$' + encrypted_text_msg

def decrypt(args):
    """
    The `decrypt` function takes an encrypted text and decrypts it using the ShieldCipher algorithm.
    
    :param args: The `args` parameter is a list of arguments passed to the `decrypt` function. In this
    case, it is expected to contain a single argument, which is the encrypted text that needs to be
    decrypted
    :return: the decrypted text.
    """
    if not args:
        msc()
        return "Usage: ShieldCipher decrypt \"text\""
        
    secret = getpass()
    encrypted_text = args[0]

    encrypted = encrypted_text.split('$')
    algorithm = encrypted[0]
    length = int(encrypted[1])
    salt = binascii.unhexlify(encrypted[2].encode('utf-8'))
    hashed = binascii.unhexlify(encrypted[3].encode('utf-8'))

    decrypted_text = sc_decrypt(secret, hashed, salt, algorithm, length)

    return decrypted_text

def main():
    """
    The main function is a command-line interface for the ShieldCipher program, allowing users to
    encrypt and decrypt text using different algorithms and options.
    """
    if len(sys.argv) < 2:
        msc()
        print("Usage: --help")
        sys.exit(1)

    action = sys.argv[1]

    if action == "--version":
        msc()
        print("ShieldCipher Version 1.0.0")
        sys.exit(0)
    elif action == "--help":
        msc()
        print("Usage: ShieldCipher <action> [args]")
        print("Actions:")
        print("  encrypt \"text\" <options>        Encrypts the provided text")
        print("    -a --algorithm        Choose the algorithm")
        print("    -l --length        Choose the length in bits")
        print("  decrypt \"text\"        Decrypts the provided text")
        print("  --version        Displays the version information")
        print("  --help        Displays this help message")
        sys.exit(0)

    args = sys.argv[2:]

    if action == "encrypt":
        result = encrypt(args)
        print(result)
    elif action == "decrypt":
        result = decrypt(args)
        print(result)
    else:
        print("Invalid action. Use '--help'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
