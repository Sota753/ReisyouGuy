import os
from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

try:
    client = AzureOpenAI(
      azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key=os.getenv("AZURE_OPENAI_KEY"),
      api_version="2024-02-01"
    )
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
except Exception as e:
    print(f"環境変数の読み込み中にエラーが発生しました: {e}")
    client = None
    deployment_name = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not client:
        return jsonify({'error': 'Azure OpenAIクライアントが設定されていません。'}), 500

    data = request.get_json()
    
    # ★★★ フロントエンドから会話履歴(messages)を丸ごと受け取る ★★★
    messages = data.get('messages')
    temperature = data.get('temperature', 0.8)

    if not messages:
        return jsonify({'error': 'メッセージがありません。'}), 400

    try:
        # ★★★ 受け取った会話履歴をそのままAPIに渡す ★★★
        completion = client.chat.completions.create(
          model=deployment_name,
          messages=messages,
          temperature=float(temperature),
          max_tokens=4095
        )

        # AIからの最新の返信だけを抽出
        continuation = completion.choices[0].message.content
        return jsonify({'story_continuation': continuation})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)