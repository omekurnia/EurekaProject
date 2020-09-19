from flask import Flask, render_template, request, redirect, url_for, session
import tweepy
from readandtwit import check_media
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "secret"

sched = BackgroundScheduler(daemon=True)
sched.add_job(check_media, 'interval', seconds=150, max_instances=2)
sched.start()

def new_keyword(kword):
    with open("keyword.txt", "w") as file:
        file.write(kword)

def check_keyword():
    with open("keyword.txt", "r") as file:
        kword = file.read()
        return kword

@app.route("/", methods=["GET", "POST"])
def index():
    kword = check_keyword()
    
    if request.method == "POST":
        kword = request.form.get("keyword")
        new_keyword(kword)

    return render_template("index.html", kword=kword)

if __name__ == "__main__":
    app.run(debug=True)