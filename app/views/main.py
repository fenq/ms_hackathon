from flask import render_template, jsonify, request
from app import app, models, db
import random

from flask import request, flash, get_flashed_messages

from flask import Flask, render_template, request
from werkzeug import secure_filename
import os.path as op
import os
import base64
from hashlib import md5
from time import localtime
from flask_login import current_user
from sqlalchemy import and_

from random import randint

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html',
            t=randint(1,9999), title="Home")
    # return render_template('index.html', title='Home')

@app.route('/select_story')
def select_story():
    return render_template('select_story.html',
            t=randint(1,9999), title="Select Story")


@app.route('/emote')
def emote():
    return render_template('emote.html',
            t=randint(1,9999), title="Select Story")

@app.route('/home')
def home():
    return render_template('home.html',
            t=randint(1,9999), title="Home")
    # return render_template('index.html', title='Home')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', title='Analytics')

@app.route('/face')
def face():
    return render_template('face.html', title='Face')

@app.route('/face2')
def face2():
    return render_template('face2.html', title='Face2')

@app.route('/map')
def map():
    return render_template('map.html', title='Map')


@app.route('/map/refresh', methods=['POST'])
def map_refresh():
    points = [(random.uniform(48.8434100, 48.8634100),
               random.uniform(2.3388000, 2.3588000))
              for _ in range(random.randint(2, 9))]
    return jsonify({'points': points})


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   	if request.method == 'POST':
   		f = request.files['file']
   		path = op.join(op.dirname(__file__), '../static/uploads/', f.filename)
   		f.save(path)
   		return "successful"

def convert_and_save(b64_string):
    b64_string = b64_string[22:]
    missing_padding = len(b64_string) % 4
    if missing_padding != 0:
        b64_string += str(b'='* (4 - missing_padding))

    name = md5(str(localtime()).encode('utf-8')).hexdigest()+'.png'
    path = op.join(op.dirname(__file__), '../static/uploads/', name)
    with open(path, "wb") as fh:
           fh.write(base64.decodebytes(str.encode(b64_string)))
    return name

@app.route('/cam', methods = ['GET','POST'])
def cam():
    if (request.method=="POST"):
        f = request.form['file']
        name = convert_and_save(f)
        userid = current_user.get_id()
        cate = request.form["cate"]

        p = models.Picture(
            user_id=userid,
            tag=cate,
            image_path=name,
            verified=None
        )
        db.session.add(p)
        db.session.commit()
    return render_template('cam.html', title='Cam')

@app.route('/label_task', methods = ['GET', 'POST'])
def label():

    if request.method == 'GET':
        # retrieve the image from the database
        p = models.Picture.query.filter_by(verified=None).first()
        if p is not None:
            #     p = models.Picture.query.filter_by().first()
            img_addr = op.join('static/uploads/', p.image_path)
            category = p.tag
            print("11 img_path: " + img_addr + " cat: " + category)
        else:
            img_addr = ""
            category = ""
    else:
        p = models.Picture.query.filter_by(verified=None).first()
        if p is not None:
            img_addr = op.join('static/uploads/', p.image_path)
            category = p.tag
            print("23 img_path: " + img_addr + " cat: " + category)
            
            if request.form['isCorrect'] == 'Yes':
                verified_res = True
            else:
                verified_res = False
            p.verified = verified_res
            db.session.commit()
            # add coin
            u = models.User.query.filter_by(email=current_user.get_id()).first()
            u.coins = models.Picture.query.filter_by(user_id=current_user.get_id(), verified = True).count()
            db.session.commit()
            # retrieve the image from the database
            p = models.Picture.query.filter_by(verified=None).first()
            if p is not None:
                category = p.tag
                img_addr = op.join('static/uploads/', p.image_path)
                print("24 img_path: " + img_addr + " cat: " + category + " coins: " + str(u.coins))
                return render_template('label_task.html', img_addr = img_addr, category = category)
            else:
                img_addr = ""
                category = ""
        else:
            img_addr = ""
            category = ""

    return render_template('label_task.html', img_addr = img_addr, category = category)

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    user = models.User.query.filter_by(email=current_user.get_id()).first()
    pic = models.Picture.query.filter_by(user_id=current_user.get_id()).count()
    veri = models.Picture.query.filter_by(user_id=current_user.get_id(), verified = True).count()
    photo=[]
    photos = models.Picture.query.filter_by(user_id=current_user.get_id()).all()
    for i in photos:
    	photo.append(i.image_path)
    return render_template('profile.html', user = user, pic=pic, veri=veri, photo=photo)
