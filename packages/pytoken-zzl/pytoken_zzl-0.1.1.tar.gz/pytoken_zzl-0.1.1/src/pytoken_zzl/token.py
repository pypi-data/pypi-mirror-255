
from datetime import datetime, timedelta
import random


class Token:
    def __init__(self, msg: str, date: datetime = None, expiry: datetime = None, id: int = None):
        self.msg = msg
        self.date = date if date else datetime.now()
        self.expiry = expiry if expiry else datetime.now()
        self.id = id if id else random.randint(0, 10000000)
    
    def encode(self) -> str:
        date = self.date.strftime("%Y-%m-%d %H:%M:%S")
        expiry = self.expiry.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.msg};?;{date};?;{expiry};?;{self.id}"
    
    @staticmethod
    def generate(msg: str, lifetime: int = 1):
        date = datetime.now()
        expiry = date + timedelta(days=lifetime)
        random.seed(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        id = random.randint(0, 10000000)
        return Token(msg, date, expiry, id)
    
    @staticmethod
    def decode(encoded: str):
        msg, date, expiry, id = encoded.split(";?;")
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        id = int(id)
        return Token(msg, date, expiry, id)
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expiry and datetime.now() > self.date
    
    def __str__(self):
        return f"{self.encode()}"


if __name__ == "__main__":
    msg = "test"
    token = Token.generate(msg, 1)
    print(token.encode())
    print(token.is_valid())
    print(Token.decode(token.encode()))