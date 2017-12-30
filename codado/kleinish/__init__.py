"""
Useful bits for klein development
"""
import warnings


warnings.warn("codado.kleinish is deprecated. Use crosscap instead!", DeprecationWarning)


from crosscap import openapi, urltool, openAPIDoc, enter
(openapi, urltool, openAPIDoc, enter) # for pyflakes
