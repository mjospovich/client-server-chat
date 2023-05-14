from cryptography.fernet import Fernet

#* Use the key from file key.key to encrypt the password and save it to a file
def create_pass(password):
    key = open("key.key", "rb").read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    with open("pass.key", "wb") as file:
        file.write(encrypted)


if __name__ == "__main__":
    password = input("Enter your password: ")
    create_pass(password)
    print("Password created successfully!")