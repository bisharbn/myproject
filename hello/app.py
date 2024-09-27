from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# API Key should be kept secret and preferably not hardcoded in production
openai.api_key = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_poem', methods=['POST'])
def get_poem():
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
            ]
        )
        poem = completion.choices[0].message['content']
        return jsonify({'poem': poem})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
