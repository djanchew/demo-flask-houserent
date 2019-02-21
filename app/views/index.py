from flask import render_template, session, request, redirect
from bson import ObjectId

from app.libs.helper import *
from . import view
from app import App


@view.route('/')
def index():
    current_user = session.get('current_user')
    db = App().mongo.db

    area = db.area
    provinces = area.find({"p_id": {"$eq": 1}})  # 给搜索框传省份的信息

    house_infos = db.house_info  # 连接数据库

    infos, city_name = search_info(house_infos, area)  # 搜索
    price, is_rent = get_search_detail()  # 搜索条件显示

    pagination, houses, count = page_generator(infos)  # 生成分页数据和分页器

    cal_limit()
    return render_template('index.html', locals=locals())


@view.route('/get_city/', methods=['POST'])
def get_city():
    id = request.form['id']
    db = App().mongo.db.area
    helo = db.find({"p_id": {"$eq": int(id)}})

    from bson import json_util

    return json_util.dumps(helo)


@view.route('/rent_book/', methods=["POST"])
@status_check
def rent_book(current_user):  # 1预约 2出租 0
    oid = request.form['oid']
    db = App().mongo.db.house_info

    from datetime import datetime
    now = str(datetime.now())
    result = db.find({"_id": ObjectId(oid)})
    if result[0]['is_rent'] == 1:
        return "exist"
    db.update({"_id": ObjectId(oid)}, {"$set": {"is_rent": 1, "renter": current_user + "^" + now}})
    return "ok"


@view.route('/rent_out/', methods=["GET", "POST"])
@status_check
def rent_out(current_user):
    if request.method == "POST":
        houses = App().mongo.db.house_info
        city_id = int(request.form['city_id'])
        img_name = save_post_img(houses, city_id)
        houses.insert({
            'city_id': city_id,
            'owner': current_user,
            'is_rent': 0,
            'title': request.form['title'],
            'room': request.form['room'],
            'price': request.form['price'],
            'loc': request.form['loc'],
            'img_name': img_name,
        })
        return "ok"
    area = App().mongo.db.area
    provinces = area.find({"p_id": {"$eq": 1}})
    the_house = None
    return render_template('rent_out.html', locals=locals())


@view.route('/profile/', methods=["GET", "POST"])
@status_check
def profile(current_user):
    db = App().mongo.db.user
    result = db.find_one({'username': current_user})
    if request.method == "POST":
        print(request.form)
        if result["password"] == request.form["password"]:
            db.update({'username': current_user},
                      {"$set": {
                          "password": request.form["re_password"],
                          "phone": request.form["phone"],
                          "email": request.form["email"],
                      }})
            return "ok"
        else:
            return "密码错误"
    return render_template('profile.html', locals=locals())


@view.route('/my_pub/')
@status_check
def my_pub(current_user):
    db = App().mongo.db
    house_infos = db.house_info
    infos = house_infos.find({"owner": current_user})
    pagination, houses, count = page_generator(infos, per=6)
    flag = 1
    return render_template('my_rent.html', locals=locals())


@view.route('/update_my_pub/', methods=["GET", "POST"])
@status_check
def update_my_pub(current_user):
    house_infos = App().mongo.db.house_info
    if request.method == "POST":
        f1 = request.files['house_img']
        file_name = house_infos.find_one({"_id": ObjectId(request.form['oid'])})['img_name']
        from app import settings
        f1.save(settings.BASE_DIR + "\static\house_img\\" + file_name + ".jpg")
        house_infos.update({"_id": ObjectId(request.form['oid'])},
                           {"$set": {
                               'title': request.form['title'],
                               'room': request.form['room'],
                               'price': request.form['price'],
                               'loc': request.form['loc'],
                           }})
        return "修改成功！"
    oid = request.args['oid']
    the_house = house_infos.find_one({"_id": ObjectId(oid)})
    flag = 1
    return render_template('rent_out.html', locals=locals())


@view.route('/my_rent/')
@status_check
def my_rent(current_user):
    house_infos = App().mongo.db.house_info
    infos = house_infos.find({"renter": {"$regex": current_user}})
    pagination, houses, count = page_generator(infos, per=6)
    return render_template('my_rent.html', locals=locals())


@view.route('/cancel_my_rent/')
@status_check
def cancel_my_rent(current_user):
    oid = request.args['oid']
    house_infos = App().mongo.db.house_info
    house_infos.update({"_id": ObjectId(oid)}, {"$set": {"is_rent": 0, "renter": ""}})
    return redirect('/my_rent')


@view.route('/user_admin/', methods=["GET", "POST"])
@is_root
def user_admin(current_user):
    db = App().mongo.db
    if request.method == "POST":
        the_user = request.form['name']
        db.house_info.update({"renter": {"$regex": the_user}}, {"$set": {"renter": "", "is_rent": 0}})  # 模糊查询，清除租赁信息
        db.house_info.delete_many({"owner": the_user})  # 删除发布的租房信息
        db.user.find_one_and_delete({"username": the_user})
        return "ok"
    users = db.user.find()
    return render_template("users.html", locals=locals())


@view.route('/house_admin/')
@is_root
def house_admin(current_user):
    cal_limit()
    pagination = None
    if request.args.get("username"):
        house_infos = App().mongo.db.house_info
        infos = house_infos.find({"renter": {"$regex": request.args.get("username")}})
        pagination, houses, count = page_generator(infos, per=6)
    is_admin = 1
    return render_template('my_rent.html', locals=locals())


@view.route('/confirm_rent/')
@is_root
def confirm_rent(current_user):
    oid = request.args['oid']
    house_infos = App().mongo.db.house_info
    house_infos.update({"_id": ObjectId(oid)}, {"$set": {"is_rent": 2}})
    return redirect("/house_admin/")
