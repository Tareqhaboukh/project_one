from flask import Blueprint, request, jsonify
from database import get_user_by_id, get_all_users

user_blueprint = Blueprint('user_api', __name__,  url_prefix='/api/v1/users')

@user_blueprint.route('/<int:id>', methods=['GET'])
def get_users(id):
    user = get_user_by_id(id)

    if user:
        return jsonify([user.to_dict()])
    else:
        return jsonify({"message": "User not found"}), 404

@user_blueprint.route('/', methods=['GET'])
def all_users():
    users = get_all_users()
    return jsonify([user.to_dict() for user in users])