from datetime import datetime, timedelta
import random 
import os


class Token:
    def __init__(self, msg: str, date: datetime = None, expiry: datetime = None, id: int = None):
        self.msg = msg
        self.date = date if date else datetime.now()
        self.expiry = expiry if expiry else datetime.now()
        self.id = id if id else random.randint(0, 10000000)
    
    def to_str(self) -> str:
        date = self.date.strftime("%Y-%m-%d %H:%M:%S")
        expiry = self.expiry.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.msg};?;{date};?;{expiry};?;{self.id}"
    
    @staticmethod
    def generate(msg: str, life: int = 1) -> "Token":
        date = datetime.now()
        expiry = date + timedelta(days=life)
        random.seed(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        id = random.randint(0, 10000000)
        return Token(msg, date, expiry, id)
    
    @staticmethod
    def from_str(string: str) -> "Token":
        msg, date, expiry, id = string.split(";?;")
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        id = int(id)
        return Token(msg, date, expiry, id)
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expiry and datetime.now() > self.date
    
    def __str__(self):
        return f"{self.to_str()}"


class TokenEncoder:
    def __init__(self, key: str = None):
        if not key:
            key = os.environ.get("PYTOKEN_KEY")
        if not key:
            raise Exception("Key not found in environment variables, please set PYTOKEN_KEY to a random string.")
        self.key = key
    
    def encode(self, token: Token) -> str:
        plain = token.to_str()
        encoded = ""
        for i in range(len(plain)):
            key_c = self.key[i % len(self.key)]
            encoded_c = chr(ord(plain[i]) + ord(key_c) % 256)
            encoded += encoded_c
        return encoded
    
    def decode(self, encoded: str) -> Token:
        plain = ""
        for i in range(len(encoded)):
            key_c = self.key[i % len(self.key)]
            encoded_c = chr(ord(encoded[i]) - ord(key_c) % 256)
            plain += encoded_c
        try:
            return Token.from_str(plain)
        except:
            return None
    
    def generate(self, msg: str, life: int = 1) -> str:
        token = Token.generate(msg, life)
        return self.encode(token)



if __name__ == "__main__":
    msg = "zzl"
    encoder = TokenEncoder(key="test_key")
    encoder2 = TokenEncoder(key="test_key")
    s = encoder.generate(msg, life=1)
    print(s)
    print(encoder2.decode(s))