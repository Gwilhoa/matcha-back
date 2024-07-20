import inspect

from marshmallow import fields
from utils.marshmallow_utils import BaseSchema


def content_generator(content: dict, is_file=False):
    content_type = 'application/json'
    if is_file:
        content_type = 'multipart/form-data'
    return_value = {}
    if inspect.isclass(content) and issubclass(content, BaseSchema):
        return_value[content_type] = {'schema': content.__name__}
    elif isinstance(content, dict):
        for key, value in content.items():
            if not issubclass(value.__class__, fields.Field):
                raise Exception(f"[swagger] Invalid body content for key '{key}'")
            content[key] = {'type': value.__class__.__name__.lower()}
            if is_file and value.metadata.get('type') == 'file':
                content[key] = {'type': 'string', 'format': 'binary'}
            return_value[content_type] = {
                'schema': {
                    'type': 'object',
                    'properties': content,
                }
            }
    else:
        raise Exception('[swagger] Invalid body content')
    return return_value


def handle_response(responses: dict):
    filtered_responses = {}
    for key, value in responses.items():
        if 'description' not in value:
            raise Exception(f"[swagger] Invalid response content for key '{key}'")
        response_data = {'description': value['description']}
        if 'content' in value:
            response_data['content'] = content_generator(value['content'])
        filtered_responses[key] = response_data
    return filtered_responses


def handle_body(body: dict, is_file: bool):
    filtered_body = {}
    if 'description' not in body or 'content' not in body:
        raise Exception('[swagger] Invalid body content')
    filtered_body['content'] = content_generator(body['content'], is_file)
    filtered_body['description'] = body['description']
    if filtered_body != {}:
        filtered_body['required'] = True
    return filtered_body


def handle_headers(headers: dict):
    filtered_headers = []
    for key, value in headers.items():
        if 'description' not in value or 'content' not in value:
            raise Exception(f"[swagger] Invalid header content for key '{key}'")
        header_data = {'name': key, 'in': 'header', 'description': value['description'], 'type': value.__class__.__name__.lower()}
        filtered_headers.append(header_data)
    return filtered_headers


def swagger(responses=None, body=None, headers=None, is_file=False):
    def decorator(func):
        filtered_body = {}
        filtered_responses = {}
        filtered_headers = {}
        file = {}
        if body:
            filtered_body = handle_body(body, is_file)
        if responses:
            filtered_responses = handle_response(responses)
        if headers:
            filtered_headers = handle_headers(headers)

        func._swagger_info = {
            'responses': filtered_responses or None,
            'requestBody': filtered_body or None,
            'headers': filtered_headers or None,
            'file': file or None,
        }
        return func

    return decorator
