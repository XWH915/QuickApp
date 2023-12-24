from flask import Flask, request, jsonify
from gevent import pywsgi
import json
import pymysql


app = Flask(__name__)


# 登录（http://localhost/login?phone=13767063831&password=123456）
@app.route("/login", methods=['GET'])
def login():
    res={}
    try:
        # 获取参数
        phone = request.values.get('phone')
        password = request.values.get('password')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM USER WHERE PHONE='%s'" % (phone))
        # 获取数据
        data = cursor.fetchone()
        # 关闭连接
        db.close()

        if data==None:
            res = {
                'code': 1,
                'data': {
                    'result': False,
                    'message': '该手机号尚未注册'
                },
                'message': ''
            }
        else:
            if data[3]==password:
                res = {
                    'code': 1,
                    'data': {
                        'result': True,
                        'message': '登录成功',
                        "userid": data[0],
                        "username": data[1]
                    },
                    'message': ''
                }
            else:
                res = {
                    'code': 1,
                    'data': {
                        'result': False,
                        'message': '密码错误'
                    },
                    'message': ''
                }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 注册（http://localhost/register?username=TEST&phone=11111111111&password=111111）
@app.route("/register", methods=['GET'])
def register():
    res={}
    try:
        # 获取参数
        username = request.values.get('username')
        phone = request.values.get('phone')
        password = request.values.get('password')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO USER(USERNAME, PHONE, PASSWORD) VALUES('%s', '%s', '%s')" % (username, phone, password))
            db.commit()
        except:
            # 如果发生错误则回滚
            db.rollback()

            res = {
                'code': 1,
                'data': {
                    'result': False,
                    'message': '该手机号已被注册，请登录'
                },
                'message': ''
            }
            return json.dumps(res, ensure_ascii=False)
        # 关闭连接
        db.close()

        res = {
            'code': 1, 
            'data': {
                'result': True,
                'message': '注册成功'
            },
            'message': ''
        }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 发帖（http://localhost/addPost?title=test&content=testtest&userid=10&username=TEST）
@app.route("/addPost", methods=['GET'])
def addPost():
    res={}
    try:
        # 获取参数
        title = request.values.get('title')
        content = request.values.get('content')
        userid = request.values.get('userid')
        username = request.values.get('username')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        cursor.execute("INSERT INTO POST(TITLE, CONTENT, USERID, USERNAME) VALUES('%s', '%s', '%s', '%s')" % (title, content, userid, username))
        postid=cursor.lastrowid
        db.commit()
        # 关闭连接
        db.close()

        res = {
            'code': 1, 
            'data': {
                'result': True,
                'message': '发帖成功',
                'postid': postid
            },
            'message': ''
        }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 获取所有帖子（http://localhost/getAllPosts)
@app.route("/getAllPosts", methods=['GET'])
def getAllPosts():
    res={}
    try:
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM POST")
        # 获取数据
        data = cursor.fetchall()
        # 关闭连接
        db.close()

        posts=[]
        for row in data:
            post={
                "postId": row[0],
                "title": row[1],
                "content": row[2],
                "userId": row[3],
                "userName": row[4],
                "time": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "finished": row[6],
            }
            posts.append(post)

        res = {
            'code': 1, 
            'data': {
                'posts': posts
            },
            'message': ''
        }
        return jsonify(res)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 搜索（http://localhost/search?keyword=你好）
@app.route("/search", methods=['GET'])
def search():
    res={}
    try:
        # 获取参数
        keyword = request.values.get('keyword')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        if "http://pinbei/post/detail/" in keyword:
            # 帖子链接
            postId=keyword[keyword.find("http://pinbei/post/detail/")+len("http://pinbei/post/detail/"):]
            cursor.execute("SELECT * FROM POST WHERE POSTID='%s'" % (postId))
        else:
            cursor.execute("SELECT * FROM POST WHERE TITLE LIKE '%" + keyword + "%' OR CONTENT LIKE '%" + keyword + "%'")
        # 获取数据
        data = cursor.fetchall()
        # 关闭连接
        db.close()

        posts=[]
        for row in data:
            post={
                "postId": row[0],
                "title": row[1],
                "content": row[2],
                "userId": row[3],
                "userName": row[4],
                "time": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "finished": row[6],
            }
            posts.append(post)

        res = {
            'code': 1, 
            'data': {
                'posts': posts
            },
            'message': ''
        }
        return jsonify(res)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 获取特定帖子详情（http://localhost/getPost?postid=6）
@app.route("/getPost", methods=['GET'])
def getPost():
    res={}
    try:
        # 获取参数
        postid = request.values.get('postid')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        # 获取帖子信息
        cursor.execute("SELECT * FROM POST WHERE POSTID='%s'" % (postid))
        data = cursor.fetchone()
        # 获取评论信息
        cursor.execute("SELECT * FROM COMMENT WHERE POSTID='%s'" % (postid))
        data1 = cursor.fetchall()
        # 关闭连接
        db.close()

        comments=[]
        for row in data1:
            comment={
                "commentId": row[0],
                "comment": row[1],
                "userId": row[2],
                "userName": row[3],
                "time": row[4].strftime('%Y-%m-%d %H:%M:%S'),
                "postId": row[5],
            }
            comments.append(comment)

        post={
            "postId": data[0],
            "title": data[1],
            "content": data[2],
            "userId": data[3],
            "userName": data[4],
            "time": data[5].strftime('%Y-%m-%d %H:%M:%S'),
            "finished": data[6],
            "comments": comments
        }

        res = {
            'code': 1, 
            'data': {
                'post': post
            },
            'message': ''
        }
        return jsonify(res)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 评价（http://localhost/comment?comment=test&userid=1&username=XWH&postid=6）
@app.route("/comment", methods=['GET'])
def comment():
    res={}
    try:
        # 获取参数
        comment = request.values.get('comment')
        userid = request.values.get('userid')
        username = request.values.get('username')
        postid = request.values.get('postid')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        cursor.execute("INSERT INTO COMMENT(COMMENT, USERID, USERNAME, POSTID) VALUES('%s', '%s', '%s', '%s')" % (comment, userid, username, postid))
        db.commit()
        # 关闭连接
        db.close()

        res = {
            'code': 1, 
            'data': {
                'result': True,
                'message': '评论成功'
            },
            'message': ''
        }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


# 修改帖子状态（http://localhost/switchPostStatus?postid=1）
@app.route("/switchPostStatus", methods=['GET'])
def switchPostStatus():
    res={}
    try:
        # 获取参数
        postid = request.values.get('postid')
        # 连接数据库并执行sql语句
        db = pymysql.connect(host='localhost', user='root', passwd='000000', port=3306, db='pinbei')
        cursor = db.cursor()
        cursor.execute("UPDATE POST SET FINISHED=True WHERE POSTID='%s'" % (postid))
        db.commit()
        # 关闭连接
        db.close()

        res = {
            'code': 1, 
            'data': {
                'result': True,
                'message': '修改成功'
            },
            'message': ''
        }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()