from flask import jsonify

def success_response(data, message=None, status_code=200):
    response = {'project': data}
    if message:
        response['message'] = message
    return jsonify(response), status_code

def list_response(projects, status_code=200):
    return jsonify({'projects': projects, 'count': len(projects)}), status_code

def error_response(message, status_code=400):
    return jsonify({'error': message}), status_code