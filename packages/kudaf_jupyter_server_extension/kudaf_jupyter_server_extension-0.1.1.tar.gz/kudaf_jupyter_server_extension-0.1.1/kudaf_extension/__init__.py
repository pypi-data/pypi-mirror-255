from kudaf_extension.app import KudafExtensionApp
from kudaf_extension.notebook import kudaf_notebook

def _jupyter_server_extension_points():
    return [
        {
            "module": "kudaf_extension.app",
            "app": KudafExtensionApp
        }
    ]
