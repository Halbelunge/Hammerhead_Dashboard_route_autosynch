import keyring

def main():
    try:
        keyring.set_password('Hammerhead','enter your username here','enter your password here')
        print('Your password is now safed')
    except:
        print('Your password was not able to be set')

if __name__ == '__main__':
    main()
