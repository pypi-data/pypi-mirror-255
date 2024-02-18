# gateway_4d_viewer
This repository hosts a simple flask app that serves data from various sources to Earthwave's 4d viewer client.

The package is typically run via gunicorn inside a container with the likes of google cloud run but can be downloaded
and run independently - such as within a juptyhub environemnt.

For core API definition, see gateway_4d_viewer/routes*.py.

For help with this package please e-mail support@earthwave.co.uk
