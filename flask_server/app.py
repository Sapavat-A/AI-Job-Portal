# class Config:
    # SECRET_KEY = "secret"
    # SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)