from flask import Flask, request, render_template, redirect
from ip import get_ip
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.user import User
from forms.register_form import RegisterForm
from data.paste import Paste


app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
hash_password = '7cb8fa366d774761d198d3dc6244740c'
my_ip = get_ip()
port = 8080
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/check", methods=["POST"])
def check():
    db_sess = db_session.create_session()
    mess = db_sess.query(Paste).filter(Paste.id == request.form["id_mess"]).first()
    if mess.check_password(request.form["password"]):
        return render_template("watching.html", message=mess, href=f"http://{my_ip}:{port}/{mess.id}")
    else:
        return render_template("check.html", message=mess, error="Bad password")
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)   
    
    
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route("/main", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return render_template("main.html", title='главная')
    else:
        db_sess = db_session.create_session()
        new_paste = Paste()
        if current_user.is_authenticated:
            new_paste.name_sender = current_user.name
        else:
            new_paste.name_sender = "Анонимный пользователь"
            
        print(request.form.getlist('secret'))
        if request.form.getlist('secret')!= list():
            new_paste.secret = 1
            new_paste.set_password(request.form["password"])
        print(request.form["about"])
        new_paste.message = request.form["about"]
        db_sess.add(new_paste)
        db_sess.commit()
        return redirect(f"/{new_paste.id}")
    
    
@app.route("/<int:id_mess>")
def watching(id_mess):
    db_sess = db_session.create_session()
    mess = db_sess.query(Paste).filter(Paste.id == id_mess).first()
    if mess.secret:
        return render_template("check.html", message=mess)
    return render_template("watching.html", message=mess, href=f"http://{my_ip}:{port}/{id_mess}")
    
    
if __name__ == "__main__":
    db_session.global_init('db/master_paste.db')
    app.run(host=my_ip, debug=True, port=port) 
