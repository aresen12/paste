from flask import Flask, request, render_template, redirect
from ip import get_ip
from data import db_session
from data.paste import Paste
app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
hash_password = '7cb8fa366d774761d198d3dc6244740c'
my_ip = get_ip()
port = 8080

@app.route("/main")
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return render_template("main.html", title='главная')
    else:
        db_sess = db_session.create_session()
        new_paste = Paste()
        print(request.form["about"])
        new_paste.message = request.form["about"]
        db_sess.add(new_paste)
        db_sess.commit()
        return redirect(f"/{new_paste.id}")
    
    
@app.route("/<int:id_mess>")
def watching(id_mess):
    db_sess = db_session.create_session()
    mess = db_sess.query(Paste).filter(Paste.id == id_mess).first()
    print(mess.message)
    return render_template("watching.html", message=mess, href=f"http://{my_ip}:{port}/{id_mess}")
    
    
if __name__ == "__main__":
    db_session.global_init('db/master_paste.db')
    app.run(host=my_ip, debug=True, port=port) 
