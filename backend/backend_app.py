from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort and sort not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'"}), 400

    if direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'"}), 400

    sorted_posts = POSTS.copy()

    if sort:
        sorted_posts = sorted(sorted_posts, key=lambda post: post[sort], reverse=(direction == 'desc'))

    return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    if not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    new_id = max(post['id'] for post in POSTS) + 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)

    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found"}), 404

    data = request.get_json()
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

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
