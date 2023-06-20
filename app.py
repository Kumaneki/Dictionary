from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    jsonify
)
from pymongo import MongoClient
import requests
from datetime import datetime

app = Flask(__name__)

cxn_str = 'mongodb+srv://MGhaniG:ghazali1503@cluster0.qplqnh2.mongodb.net/'
client = MongoClient(cxn_str)

db = client.dbsparta_plus_week2

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg = request.args.get('msg')
    return render_template(
        'index.html',
        words=words,
        msg=msg
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    status = request.args.get('status_give','new')
    api_key = "da02232e-8495-4419-8fd5-276a6dba55ae"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for('erno', word=keyword))

    if type(definitions[0]) is str:
        suggestions = ','.join(definitions)
        # return direct(url_for('index',msg=f'Could not find the word)
        return redirect(url_for('main', word=keyword,suggests=suggestions ))
    # return render_template('index.html', word=keyword, definitions=definitions,status=status)


    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d'),
    }

    db.words.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was deleted',
    })

@app.route('/error')
def erno():
    word = request.args.get('word')
    if 'suggests' not in request.args:
        return render_template('error.html',word=word)
    else:
        suggestions = request.args.get('suggests')
        suggests = suggestions.split(',')
        return render_template('error.html',word=word,suggests=suggests)
    
@app.route('/api/get_ex',methods=['GET'])
def get_ex():
    word = request.args.get('word')
    example_data = db.examples.find({'word':word})
    examples = []
    for example in example_data:
        examples.append({
            'example':example.get('example'),
            'id':str(example.get('_id')),
        })
    return jsonify({'status':'success','examples':examples})

@app.route('/api/save_ex',methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word':word,
        'example':example,
    }
    db.examples.insert_one(doc)
    return jsonify({'status':'success','msg':f'example of the word {word}, was saved'})

@app.route('/api/del_ex',methods=['POST'])
def del_ex():
    word = request.form.get('word')
    id = request.form.get('id')
    db.examples.delete_one({'_id':ObjectId(id)})
    return jsonify({'status':'success','msg':f'example of the word {word}, was deleted'})

@app.errorhandler(404)
def page_not_found(e):
    message = 'Oops, you are not supposed to be here'
    return render_template('error.html',message=message)

# @app.route('/practice')
# def practice():
#     return render_template('practice.html')

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000,debug=True)