from flask import session, request

from app.libs.validate import RegisterValidate


def login_check(db, account, pwd, remember):
    if db.find_one({"username": account}):
        result = db.find_one({"username": account})
    else:
        return '用户名不存在'
    return password_check(result, pwd, remember)


def password_check(result, pwd, remember):
    if pwd == result['password']:
        session['current_user'] = result['username']
        if remember:
            session.permanent = True
        return 'ok'
    else:
        return 'error'


def register_check(result, db):
    if result:
        return 'exist'
    else:
        forms = RegisterValidate(request.form)
        if forms.validate():
            db.insert({
                "username": request.form['username'],
                "password": request.form['password'],
                "email": request.form['email'],
                "phone": request.form['phone'],
            })
            session['current_user'] = request.form['username']
            return 'ok'
        else:
            return str(forms.errors)
