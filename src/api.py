import uuid 

from flask import Flask, request, jsonify, abort


# initialize Flask server
app = Flask(__name__)

# create unique id for lists, entries
todo_list_1_id = '1318d3d1-d979-47e1-a225-dab1751dbe75'
todo_list_2_id = '3062dc25-6b80-4315-bb1d-a7c86b014c65'
todo_list_3_id = '44b02e00-03bc-451d-8d01-0c67ea866fee'
todo_1_id = str(uuid.uuid4())
todo_2_id = str(uuid.uuid4())
todo_3_id = str(uuid.uuid4())
todo_4_id = str(uuid.uuid4())
user_1_id = str(uuid.uuid4())
user_2_id = str(uuid.uuid4())
user_3_id = str(uuid.uuid4())
user_4_id = str(uuid.uuid4())

# define internal data structures with example data
todo_lists = [
    {'id': todo_list_1_id, 'name': 'Einkaufsliste'},
    {'id': todo_list_2_id, 'name': 'Arbeit'},
    {'id': todo_list_3_id, 'name': 'Privat'},
]
todos = [
    {'id': todo_1_id, 'name': 'Milch', 'description': 'Einkaufslisteneintrag', 'list_id': todo_list_1_id, 'user_id': user_1_id},
    {'id': todo_2_id, 'name': 'Arbeitsblätter ausdrucken', 'description': 'Einkaufslisteneintrag', 'list_id': todo_list_2_id, 'user_id': user_1_id},
    {'id': todo_3_id, 'name': 'Kinokarten kaufen', 'description': 'Einkaufslisteneintrag', 'list_id': todo_list_3_id, 'user_id': user_1_id},
    {'id': todo_4_id, 'name': 'Eier', 'description': 'Einkaufslisteneintrag', 'list_id': todo_list_1_id, 'user_id': user_1_id},
] 

# add some headers to allow cross origin access to the API on this server, necessary for using preview in Swagger Editor!
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# define endpoint for getting and deleting existing lists
@app.route('/todo-list/<list_id>', methods=['GET', 'DELETE'])
def handle_list(list_id):
    # find todo list depending on given list id
    list_item = None
    for l in todo_lists:
        if l['id'] == list_id:
            list_item = l
            break
    # if the given list id is invalid, return status code 404
    if not list_item:
        abort(404)
    if request.method == 'GET':
        # find all todo entries for the todo list with the given id
        print('Returning todo list...')
        return jsonify([i for i in todo_lists if i['id'] == list_id])
    elif request.method == 'DELETE':
        # delete list with given id
        print('Deleting todo list...')
        todo_lists.remove(list_item)
        return '', 200
    else: abort(405) 


# define endpoint for adding a new list
@app.route('/todo-list', methods=['POST'])
def add_new_list():
    if request.method == 'POST':
        # make JSON from POST data (even if content type is not set correctly)
        new_list = request.get_json(force=True)
        print('Got new list to be added: {}'.format(new_list))
        # create id for new list, save it and return the list with id
        new_list['id'] = uuid.uuid4()
        todo_lists.append(new_list)
        return jsonify(new_list), 200
    else: abort(405)

# define endpoint for getting all lists
@app.route('/todo-lists', methods=['GET'])
def get_all_lists():
    if request.method == 'GET':
        return jsonify(todo_lists)
    else: abort(405)

@app.route('/todo-list/<list_id>/entries', methods=['GET'])
def get_all_todos_for_list(list_id):
    if not any(l['id'] == list_id for l in todo_lists):
        abort(404)
    if request.method == 'GET': 
        temp_todos = []
        for t in todos:
            print(t)
            if t['list_id'] == list_id:
                temp_todos.append(t)
        return jsonify(temp_todos), 200
    else: abort(405)
    
@app.route('/todo-list/<list_id>/entry', methods=['POST'])
def add_entry(list_id):
    if not any(l['id'] == list_id for l in todo_lists):
        abort(404)
    if request.method == 'POST':  
        new_entry = request.get_json(force=True)
        new_entry['id'] = str(uuid.uuid4())
        new_entry['list_id'] = list_id
        todos.append(new_entry)
        return jsonify(new_entry), 200
    else: abort(405)

@app.route('/todo-list/<list_id>/entry/<entry_id>', methods=['PUT', 'DELETE'])
def handle_entry(list_id, entry_id):
    list_id = str(list_id) 
    entry_id = str(entry_id)

    if not any(str(l['id']) == list_id for l in todo_lists) or not any(str(t['id']) == entry_id for t in todos):
        abort(404)

    todo_entry = next((t for t in todos if str(t['id']) == entry_id and str(t['list_id']) == list_id), None)

    if request.method == 'PUT':
        if not todo_entry:
            abort(404)
        data = request.get_json(force=True)
        todo_entry.update(data)
        return jsonify(todo_entry)

    if request.method == 'DELETE': 
        print('Deleting todo...')
        todos.remove(todo_entry)
        return '', 200
    
    else: abort(405)

if __name__ == '__main__':
    # start Flask server
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
