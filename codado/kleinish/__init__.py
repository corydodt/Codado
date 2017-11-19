"""
Useful bits for klein development
"""
import yaml

from codado.kleinish import openapi, urltool

yaml.add_representer(openapi.OpenAPIResponse, openapi.representCleanOpenAPIObjects)
yaml.add_representer(openapi.OpenAPIResponses, openapi.representCleanOpenAPIObjects)
yaml.add_representer(openapi.OpenAPIMediaType, openapi.representCleanOpenAPIObjects)
yaml.add_representer(openapi.OpenAPIPathItem, openapi.representCleanOpenAPIPathItem)
yaml.add_representer(openapi.OpenAPIOperation, openapi.representCleanOpenAPIOperation)
yaml.add_representer(openapi.OpenAPI, openapi.representCleanOpenAPIObjects)
yaml.add_representer(openapi.OpenAPIInfo, openapi.representCleanOpenAPIObjects)
yaml.add_representer(openapi.UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)

yaml.add_representer(unicode, urltool.literal_unicode_representer)
yaml.add_representer(str, urltool.literal_unicode_representer)

from codado.kleinish.tree import openAPIDoc, enter
(openAPIDoc, enter) # for pyflakes
