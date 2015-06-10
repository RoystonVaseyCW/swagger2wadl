__author__ = 'chris'

import sys, urllib3, json, re
import xml.etree.ElementTree as tree

def camel_case(value):
    words = value.split("_")
    return ''.join([words[0]] + list(word.title() for word in words[1:]))

def add_request(parent, parameters):
    try:
        data_type = list(request['dataType'] for request in parameters if request['paramType'] == 'body').pop()
    except:
        data_type = None

    request = tree.SubElement(parent, 'request')
    add_parameters(request, parameters)

    if data_type is not None:
        tree.SubElement(request, 'representation', {"mediaType": "application/json", "json:describedBy": data_type})


def add_responses(parent, responses):
    """Add responses"""
    success = ' '.join(str(response['code']) for response in responses if response['code'] < 400)
    failure = ' '.join(str(response['code']) for response in responses if response['code'] >= 400 and response['code'] != 404)
    not_found = ' '.join(str(response['code']) for response in responses if response['code'] == 404)

    response = tree.SubElement(parent, 'response', {'status': success})
    tree.SubElement(response, 'representation', {'mediaType': 'application/json'})

    response = tree.SubElement(parent, 'response', {'status': failure})
    tree.SubElement(response, 'representation', {'mediaType': 'application/json'})

    tree.SubElement(parent, 'response', {'status': "401" + (" 404" if not_found else "")})

def add_parameters(parent, parameters):
    for param in parameters:
        param_name = camel_case(param['name'])
        required = str(param['required']).lower()
        #parameter = parent.find('.//param[@name="%s"]'% param_name)

        #if parameter is None:
        if param['paramType'] not in ['body', 'path']:
            tree.SubElement(parent, 'param',
                                {'name': param_name,
                                 'style': param['paramType'],
                                 'required': required})
        #else:
        #    """Make sure that query parameters are made optional if they need to be
        #    Necessary evil given differences between parameter setting in Swagger and WADL"""
        #    if 'required' in parameter.attrib and parameter.attrib['required'] == 'true' and required == 'false':
        #        parameter.attrib['required'] = required

def add_operations(parent, operations):
    for operation in operations:
        method = tree.SubElement(parent, 'method', {'name': operation['method'].upper()})

        if 'notes' in operation:
            doc = tree.SubElement(method, 'doc')
            doc.text = operation['notes']

        add_request(method, operation['parameters'])
        add_responses(method, operation['responseMessages'])

def create_wadl(spec, endpoint):
    wadl = tree.Element('application')
    doc = tree.SubElement(wadl,'doc')
    paths = list(api['path'] for api in spec['apis'])

    if 'description' in spec:
        doc.text = spec['description']
    resources = tree.SubElement(wadl, 'resources', {'base': endpoint + spec['resourcePath']})

    """Loop through the APIs and add as resources.
    Any template-style parameters needs to be added as param and resource"""
    for api in spec['apis']:
        """Check whether this includes a template-style parameter. If it does, process as resource and param"""
        param = re.search(r'/\{(.+?)\}', api['path'])

        if param is not None:
            raw_param = param.group().replace("/","")
            parent_path = re.sub('^/|/$','',api['path'].replace(raw_param,''))
            resource = tree.SubElement(resources, 'resource', {'path': parent_path})

            """if '/' + parent_path in paths:
                add_parameters(resource,
                               list(api for api in spec['apis'] if api['path'] == '/' + parent_path).pop()['operations'])"""

            param = camel_case(param.group().replace("/",""))
            template = tree.SubElement(resource, 'resource', {'path': param})
            tree.SubElement(template, 'param',
                            {'path': re.sub('(\{|\})','',param), 'style': 'template', 'required': 'true'})
            add_operations(template, api['operations'])

        else:
            path = re.sub('^/', '', api['path'])
            resource = wadl.find('.//resource[@path="' + path + '"]')

            if resource is None:
                resource = tree.SubElement(resources, 'resource', {'path': re.sub('^/', '', api['path'])})

            add_operations(resource, api['operations'])

    wadl.set('xmlns', 'http://wadl.dev.java.net/2009/02')
    wadl.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    wadl.set('xsi:schemaLocation', 'http://wadl.dev.java.net/2009/02 http://www.w3.org/Submission/wadl/wadl.xsd')
    wadl.set("xmlns:json", "http://wadl.dev.java.net/2009/02/json-schema")

    tree.dump(wadl)

def main():
    try:
        spec_url, endpoint = sys.argv[1], sys.argv[2]

    except:
        raise Exception('Missing parameters: [spec url]')

    manager = urllib3.PoolManager()
    spec = json.loads(manager.urlopen('GET', spec_url).data.decode("utf-8"))
    create_wadl(spec, endpoint)

if __name__ == "__main__":
    main()
