from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': 'Masterblog API'}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def load_posts():
    with open('posts.json', 'r') as f:
        return json.load(f)

def save_posts(posts):
    with open('posts.json', 'w') as f:
        json.dump(posts, f)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = load_posts()
    sort = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort and sort not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field"}), 400

    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction"}), 400

    if sort:
        posts = sorted(posts, key=lambda post: post[sort], reverse=(direction == 'desc'))

    return jsonify(posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    posts = load_posts()
    data = request.get_json()

    if not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    new_id = max(post['id'] for post in posts) + 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    posts.append(new_post)
    save_posts(posts)
    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    posts.remove(post)
    save_posts(posts)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

    save_posts(posts)
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    results = [
        post for post in POSTS
        if (title and title.lower() in post['title'].lower())
           or (content and content.lower() in post['content'].lower())
    ]

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
