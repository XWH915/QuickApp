from flask import Flask
from gevent import pywsgi
import json


app = Flask(__name__)


@app.route("/test", methods=['GET'])
def test():
    try:
        res = {
            'code': 1,
            'data': {},
            'message': '获取成功'
        }
        return json.dumps(res, ensure_ascii=False)
    except:
        res = {'code': -1, 'message': '服务器发生未知错误，请稍后重试'}
        return json.dumps(res, ensure_ascii=False)
    

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()