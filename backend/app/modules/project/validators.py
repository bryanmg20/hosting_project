def validate_create_project_data(data):
    if not data:
        return {'valid': False, 'error': 'No JSON data provided'}
    
    required_fields = ['name', 'github_url', 'template']
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'error': f'Missing required field: {field}'}
    
    name = data['name']
    github_url = data['github_url']
    template = data['template']
    
    if not name or not isinstance(name, str):
        return {'valid': False, 'error': 'Name must be a non-empty string'}
    
    if not github_url or not isinstance(github_url, str):
        return {'valid': False, 'error': 'GitHub URL must be a non-empty string'}
    
    valid_templates = ['react', 'static', 'flask']
    if template not in valid_templates:
        return {'valid': False, 'error': f'Invalid template. Must be one of: {", ".join(valid_templates)}'}
    
    return {'valid': True, 'name': name, 'github_url': github_url, 'template': template}

def validate_project_status(data):
    if 'status' not in data:
        return {'valid': False, 'error': 'Missing status field'}
    
    valid_statuses = ['deploying', 'active', 'failed', 'deleting']
    if data['status'] not in valid_statuses:
        return {'valid': False, 'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}
    
    return {'valid': True, 'status': data['status']}