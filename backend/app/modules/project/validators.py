def validate_create_project_data(data):
    if not data:
        return {'valid': False, 'error': 'No JSON data provided'}
    
    required_fields = ['name', 'github_url']
    for field in required_fields:
        if field not in data:
            return {'valid': False, 'error': f'Missing required field: {field}'}
    
    name = data['name']
    github_url = data['github_url']
    
    if not name or not isinstance(name, str):
        return {'valid': False, 'error': 'Name must be a non-empty string'}
    
    if not github_url or not isinstance(github_url, str):
        return {'valid': False, 'error': 'GitHub URL must be a non-empty string'}
    
    return {'valid': True, 'name': name, 'github_url': github_url}

