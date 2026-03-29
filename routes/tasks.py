from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import Task

tasks_bp = Blueprint('tasks', __name__)

VALID_STATUSES = ['pending', 'in_progress', 'done']
VALID_PRIORITIES = ['low', 'medium', 'high']

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get('role') == 'admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(user_id=user_id).all()

    return jsonify({
        'tasks': [t.to_dict() for t in tasks],
        'count': len(tasks)
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    task = Task.query.get_or_404(task_id)

    if claims.get('role') != 'admin' and str(task.user_id) != str(user_id):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'task': task.to_dict()}), 200


@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    if len(data['title'].strip()) == 0:
        return jsonify({'error': 'Title cannot be empty'}), 400

    status = data.get('status', 'pending')
    priority = data.get('priority', 'medium')

    if status not in VALID_STATUSES:
        return jsonify({'error': f'Status must be one of {VALID_STATUSES}'}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({'error': f'Priority must be one of {VALID_PRIORITIES}'}), 400

    task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    task = Task.query.get_or_404(task_id)

    if claims.get('role') != 'admin' and str(task.user_id) != str(user_id):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'title' in data:
        if not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
        task.title = data['title'].strip()
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'Status must be one of {VALID_STATUSES}'}), 400
        task.status = data['status']
    if 'priority' in data:
        if data['priority'] not in VALID_PRIORITIES:
            return jsonify({'error': f'Priority must be one of {VALID_PRIORITIES}'}), 400
        task.priority = data['priority']

    db.session.commit()
    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    task = Task.query.get_or_404(task_id)

    if claims.get('role') != 'admin' and str(task.user_id) != str(user_id):
        return jsonify({'error': 'Access denied'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200
