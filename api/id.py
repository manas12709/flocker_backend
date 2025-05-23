from flask import Blueprint, jsonify

id_api = Blueprint('id_api', __name__, url_prefix='/api')

@id_api.route('/id', methods=['GET'])
def get_id():
    # Example response
    return jsonify({"id": 1}) 