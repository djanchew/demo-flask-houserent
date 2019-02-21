from functools import wraps

from flask import session, redirect, request

from app import App


def status_check(func):
    @wraps(func)
    def inner():
        if not session.get('current_user'):
            return 'error'
        else:
            return func(session.get('current_user'))

    return inner


def is_root(func):
    @wraps(func)
    def inner():
        if not session.get('current_user') == "root":
            return 'Permission denied. Cause: this method can only be executed by root user.'
        else:
            return func(session.get('current_user'))

    return inner


def page_generator(infos, per=6):
    from flask_paginate import Pagination, get_page_parameter
    count = infos.count()

    PER_PAGE = per

    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    pagination = Pagination(bs_version=3, page=page, total=count)

    print("--------查到%s条记录-----------" % count)
    houses = infos[start: end]

    return pagination, houses, count


def search_info(house_infos, area):
    city_id = request.args.get('city_id')
    is_rent = request.args.get('is_rent')
    price = request.args.get('price')

    if city_id or is_rent or price:  # 当有参数时分情况处理
        if city_id:
            if is_rent and price:  # 三个都有
                price_min, price_max = get_price_field(price)
                infos = house_infos.find({
                    "city_id": int(city_id),
                    "is_rent": int(is_rent),
                    '$and': [{'price': {'$gte': price_min}}, {'price': {'$lte': price_max}}]
                })
            elif is_rent:  # 只有两个
                infos = house_infos.find({
                    "city_id": int(city_id),
                    "is_rent": int(is_rent),
                })
            elif price:  # 只有两个
                price_min, price_max = get_price_field(price)
                infos = house_infos.find({
                    "city_id": int(city_id),
                    '$and': [{'price': {'$gte': price_min}}, {'price': {'$lte': price_max}}]
                })
            else:
                infos = house_infos.find({
                    "city_id": int(city_id),
                })
            city_name = area.find({"id": int(city_id)})[0]['name']
        elif is_rent:
            if price:
                price_min, price_max = get_price_field(price)
                infos = house_infos.find({
                    "is_rent": int(is_rent),
                    '$and': [{'price': {'$gte': price_min}}, {'price': {'$lte': price_max}}]
                })
            else:
                infos = house_infos.find({
                    "is_rent": int(is_rent),
                })
            city_name = '全部'
        else:
            price_min, price_max = get_price_field(price)
            infos = house_infos.find({
                '$and': [{'price': {'$gte': price_min}}, {'price': {'$lte': price_max}}]
            })
            city_name = '全部'
    else:  # 没有参数时返回全部
        infos = house_infos.find()
        city_name = '全部'

    return infos, city_name


def get_price_field(price):
    l = price.split('-')
    print(l)
    price_min = int(l[0])
    price_max = int(l[1])
    return price_min, price_max


def get_search_detail():
    price = request.args.get('price')
    is_rent = request.args.get('is_rent')
    if not price:
        price = ''
    if is_rent:
        if is_rent == '0':
            is_rent = "未出租"
        elif is_rent == '1':
            is_rent = "预约中"
        else:
            is_rent = "已出租"
    else:
        is_rent = ""
    return price, is_rent


def save_post_img(houses, city_id):  # 获取图片最大的索引
    try:
        a = houses.find({"city_id": city_id})
        a = list(a)
        int(a[-1]['img_name'].split("_")[1])
        img_index = int(a[-1]['img_name'].split("_")[1]) + 1  # 取列表最后一个，字典取值，分裂字符串获得数字
    except:
        img_index = 0
    f1 = request.files['house_img']

    file_name = (str(city_id) + '_' + str(img_index))
    from app import settings
    f1.save(settings.BASE_DIR + "\static\house_img\\" + file_name + ".jpg")  # 需要用管理员的cmd运行的服务器才可以操作写?
    return file_name


def cal_limit():
    db = App().mongo.db.house_info
    l = list(db.find())
    from datetime import datetime, timedelta
    from bson import ObjectId
    for i in l:
        try:
            a = datetime.strptime(i['renter'].split('^')[1].split('.')[0], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - a > timedelta(hours=48):
                print("-----已过48小时------------")
                db.update({"_id": ObjectId(i['_id'])}, {"$set": {"renter": "", "is_rent": 0}})
        except:
            pass
