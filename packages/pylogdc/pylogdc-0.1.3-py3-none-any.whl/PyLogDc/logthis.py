# logthis.py
import requests

def log_this(header, message, color, webhook, footer=None):
    if footer:
        footer_text = f"{footer}"
    else:
        footer_text = None

    color_code = None
    if color.startswith('#'):
        color_code = int(color[1:], 16)
    elif color.lower() == 'success':
        color_code = int("5cb85c", 16)
    elif color.lower() == 'info':
        color_code = int("5bc0de", 16)
    elif color.lower() == 'warning':
        color_code = int("f0ad4e", 16)
    elif color.lower() == 'danger':
        color_code = int("d9534f", 16)

    data = {
        "embeds": [
            {
                "title": header,
                "description": message,
                "color": color_code,
                "footer": {"text": footer_text}
            }
        ]
    }

    headers = {'Content-Type': 'application/json'}
    result = requests.post(webhook, json=data, headers=headers)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
