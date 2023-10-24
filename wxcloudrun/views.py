from datetime import datetime
from flask import render_template, request, jsonify
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import os
import openai
import requests
import json

OPENAI_API_URL = "https://api.openai.com/v1/engines/davinci/completions"
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def get_openai_suggestions(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 150
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    return response.json().get('choices')[0].get('text').strip()


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

@app.route('/api/evaluate_resume', methods=['POST'])
def evaluate_resume():

    # 打印原始请求数据和解析后的表单数据
    print(request.data)  # 打印原始请求数据
    print(request.form)  # 打印解析后的表单数据

    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # resume_text = request.form.get('resume_text')
    # if not resume_text:
    #     return jsonify({"error": "Resume text is required"}), 400

    # prompt = f"请评估以下简历内容: {resume_text}"

    # 准备请求的数据
    request_data = {
        "engine": "davinci",  # 使用gpt-3.5-turbo引擎
        "prompt": "Translate the following English text to French: 'Hello, how are you?'",  # 这里是您的输入文本
        "max_tokens": 500  # 生成的文本的最大长度
    }

    # 将请求数据转换为JSON格式
    json_data = json.dumps(request_data)

    # 设置请求的content-type为application/json
    headers = {"Content-Type": "application/json"}

    # 使用OpenAI的Completion API生成文本
    response = openai.Completion.create(data=json_data, headers=headers)


    return response.choices[0].text.strip()  # 返回生成的文本
