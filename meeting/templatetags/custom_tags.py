import json
from django import template

register = template.Library()

@register.filter(name='jsonify')
def jsonify(value):
    return json.dumps([{
        'message': message.message,
        'tags': message.tags,
    } for message in value])