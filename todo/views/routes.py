from flask import Blueprint, jsonify, request 
from todo.models import db 
from todo.models.todo import Todo 
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})





@api.route('/todos', methods=['GET'])
def get_todos():
    todo = Todo.query.all()
    result = []
    completed = request.args.get('completed', default=None)
    if completed:
        completed = completed.lower() == 'true'

    window = request.args.get('window', default=None, type=int)
    if window is not None:
        deadline_date = datetime.utcnow()+timedelta(days=window)

    for todos in todo:
        if completed is not None and todos.completed != completed:
            continue
        if window is not None and todos.deadline_at and todos.deadline_at > deadline_date:
            continue
        result.append(todos.to_dict())

    return jsonify(result)




@api.route('/todos/<int:todo_id>', methods=['GET']) #done
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify ({"error":"Todo not Found"}), 404
    return jsonify(todo.to_dict()), 200


@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    fields = {'title','description','completed','deadline_at'}
    keys_json = set(request.json.keys())
    extra_keys = keys_json - fields
    if extra_keys:
        return jsonify({"error": f"Unexpected fields: {', '.join(extra_keys)}"}), 400

    todo = Todo(
        title = request.json.get('title'),
        description = request.json.get('description'),
        completed = request.json.get('completed', False),
    )

    if todo.title is None:
        return jsonify({"error": "Title is required"}), 400
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201



@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    fields = {'title','description','completed','deadline_at'}
    keys_json = set(request.json.keys())
    extra_keys = keys_json - fields
    if extra_keys:
        return jsonify({"error": f"Unexpected fields: {', '.join(extra_keys)}"}), 400
    
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error":"Todo not found"}), 404
    if id in request.json:
        return ({"error":"Updating the ID is not allowed"}), 400
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()

    return jsonify(todo.to_dict())



@api.route('/todos/<int:todo_id>', methods=['DELETE']) #done
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error":"Todo not found"}),200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
