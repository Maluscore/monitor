import subprocess
import time
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = 'secret_key'

def log(*args):
    print(*args)

def data_from_pipe():
    # iostat 1: 表示每隔 1 秒 输出一个信息
    cmd = ['iostat 1']
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # 用生成器接住, 请求的时候才输出
    output = (line.decode('utf-8').strip() for line in pipe.stdout)
    return output

def init_db():
    client = MongoClient()
    db = client.monitor_db
    cpu_info = db.cpu_info
    cpu_labels = ['user', 'nice', 'system', 'iowait', 'steal', 'idle', ]
    cpu_d = dict(labels=cpu_labels, dataset=[])
    cpu_info.insert(cpu_d)
    return cpu_info

def data_init(output, cpu_info):
    next(output)
    index = 1
    # if index%6 == 3:
    #     cpu_collection = cpu_info.find_one()
    #     dataDict = dict(
    #     datalist = o.split(),
    #     timestamp = time.time(),
    #     )
    #     cpu_collection['dataset'].append(dataDict)
    #     cpu_info.save(cpu_collection)
    # index += 1
    for o in output:
        if index%6 == 3:
            cpu_collection = cpu_info.find_one()
            dataDict = dict(
            datalist = o.split(),
            timestamp = time.time(),
            )
            cpu_collection['dataset'].append(dataDict)
            cpu_info.save(cpu_collection)
        index += 1
    return None

def data_insert(output):
    client = MongoClient()
    db = client.monitor_db
    cpu_info = db.cpu_info
    # log('test', cpu_info.find_one())
    # if index % 6 == 3:
    #     cpu_collection = cpu_info.find_one()
    #     dataDict = dict(
    #     datalist = o.split(),
    #     timestamp = time.time(),
    #     )
    #     cpu_collection['dataset'].append(dataDict)
    #     cpu_info.save(cpu_collection)
    for o in output:
        log('ooo:', o)
        datalist = o.split()
        if len(datalist) == 6 and datalist[0] != 'sda' and datalist[0] != 'Device:':
            cpu_collection = cpu_info.find_one()
            dataDict = dict(
            datalist = o.split(),
            timestamp = time.time(),
            )
            log('dataDict:', dataDict)
            cpu_collection['dataset'].append(dataDict)
            cpu_info.save(cpu_collection)
            break
    return cpu_info


@app.route('/')
def index_view():
    return render_template('index.html')


@app.route('/update/system', methods=['POST'])
def chart_update():
    cpu_info = data_insert(output)
    form = request.get_json()
    d = cpu_info.find_one()
    dataNeeded = d['dataset']
    r = dataNeeded[-5:]
    log('r is:', r)
    return jsonify(r)

if __name__ == '__main__':
    output = data_from_pipe()
    title = next(output)
    # cpu_info = init_db()
    # data_init(output, cpu_info)
    app.run(debug=True)
