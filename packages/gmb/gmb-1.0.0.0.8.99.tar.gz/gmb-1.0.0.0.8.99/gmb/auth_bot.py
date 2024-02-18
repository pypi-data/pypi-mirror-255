from pyotp import TOTP

def guess():
    totp = TOTP('GBNQ24DU3DUH5NLSPW6XMRBHQO3BWCPK')
    while True:
        input_secret = input("Enter The Balls Code:")
        state = totp.verify(input_secret)
        if state:
            print("hello")
            break
        else:
            print("Oh, Boy The Code In Not Correct, So You Have To Eat Balls")
            print(totp.now())