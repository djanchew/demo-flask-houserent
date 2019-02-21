from app.libs.login_helper import login_check, register_check
from app.libs.validate import RegisterValidate
from . import view
from flask import request, redirect, session
from app import App


@view.route('/login/', methods=['POST'])
def login():
    print(request.form)
    if request.form.get('remember_me'):
        remember = True
    else:
        remember = False
    db = App().mongo.db.user
    return login_check(db=db, account=request.form['account'], pwd=request.form['password'],
                       remember=remember)


@view.route('/forget_pwd/', methods=['POST'])
def forget_pwd():
    username = request.form['username']
    account = request.form['account']

    db = App().mongo.db.user
    exist = db.find_one({"username": username})
    if exist:
        result = db.find_one({"$and":
                                  [{"username": username}, {"$or": [{"phone": account}, {"email": account}]}]
                              })
        if result:
            db.update({"username": result["username"]}, {"$set": {"password": "123456"}})
            return "ok"
        else:
            return "手机/邮箱输入错误，请重新输入！"
    else:
        return "用户名不存在"


@view.route('/register/', methods=['POST'])
def register():
    username = request.form['username']

    db = App().mongo.db.user
    result = db.find_one({"username": username})
    return register_check(result, db)


@view.route('/logout/')
def logout():
    session.clear()
    return redirect('/')
