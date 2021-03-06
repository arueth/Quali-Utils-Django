import xml.etree.ElementTree as etree
import http.client as http_client
from urllib.parse import urlparse
from xml.sax.saxutils import escape
import importlib
from collections import OrderedDict


class XMLWrapper:
    @staticmethod
    def parseXML(xml_str):
        return etree.fromstring(xml_str)

    @staticmethod
    def getRootNode(node):
        return node.getroot()

    @staticmethod
    def getChildNode(parent_node, child_name, find_prefix=''):
        return parent_node.find(find_prefix + child_name)

    @staticmethod
    def getAllChildNode(parent_node, child_name, find_prefix=''):
        return parent_node.findall(find_prefix + child_name)

    @staticmethod
    def getChildNodeByAttr(parent_node, child_name, attr_name, attr_value):
        return parent_node.find(child_name + '[@' + attr_name + '=\'' + attr_value + '\']')

    @staticmethod
    def getAllChildNodeByAttr(parent_node, child_name, attr_name, attr_value):
        return parent_node.findall(child_name + '[@' + attr_name + '=\'' + attr_value + '\']')

    @staticmethod
    def getNodeName(node):
        return node.tag

    @staticmethod
    def getNodeText(node):
        return node.text

    @staticmethod
    def getNodeAttr(node, attribute_name, find_prefix=''):
        return node.get(find_prefix + attribute_name)

    @staticmethod
    def getNodePrefix(node, prefix_name):
        prefix = ''
        if len(node.attrib) == 0:
            return prefix
        for attrib_name, value in node.attrib.items():
            if attrib_name[0] == "{":
                prefix, ignore, tag = attrib_name[1:].partition("}")
                return "{" + prefix + "}"

        return prefix

    @staticmethod
    def getStringFromXML(node, pretty_print=False):
        return etree.tostring(node, pretty_print=pretty_print)


# map request class
class CommonAPIRequest:
    def __init__(self, **kwarg):
        for key, value in kwarg.items():
            setattr(self, key, value)

    @staticmethod
    def _checkContainerValue(value):
        result_value = None
        if isinstance(value, list):
            result_value = list()
            for list_value in value:
                result_value.append(CommonAPIRequest.toContainer(list_value))
        elif isinstance(value, CommonAPIRequest):
            result_value = CommonAPIRequest.toContainer(value)
        else:
            result_value = value

        return result_value

    @staticmethod
    def toContainer(data):
        if isinstance(data, dict) or isinstance(data, OrderedDict):
            return data

        if isinstance(data, list):
            data_list = list()
            for value in data:
                data_list.append(CommonAPIRequest._checkContainerValue(value))
            return data_list

        data_dict = dict()
        data_dict['__name__'] = data.__class__.__name__
        for key, value in data.__dict__.items():
            data_dict[key] = CommonAPIRequest._checkContainerValue(value)

        return data_dict


# end map request class

class CommonResponseInfo:
    def _attributeCastToType(self, data_str, cast_type_name):
        default_value = 0
        if cast_type_name == 'bool':
            default_value = False
        elif cast_type_name == 'float':
            default_value = 0.0
        elif cast_type_name == 'str':
            default_value = ''

        cast_type = eval(cast_type_name)
        data = None
        if data_str is not None:
            data = default_value
            try:
                if cast_type_name == 'bool':
                    data = (data_str.lower() in ['true', '1', 'yes', 'on'])
                else:
                    data = cast_type(data_str)
            except ValueError as err:
                pass

        return data

    def _isAttributeTypeDefault(self, attr_type_name):
        return (attr_type_name == 'int' or attr_type_name == 'long' or
                attr_type_name == 'float' or attr_type_name == 'bool' or attr_type_name == 'str')

    def _is_empty_object(self, atrrib_data):
        for key, value in atrrib_data.items():
            if isinstance(value, list) and len(value) > 0:
                return False

            if value is not None:
                return False

        return True

    def _append_object_list(self, attr_type_name, list_node, attr_type_instance, class_type, find_prefix):
        if self._isAttributeTypeDefault(attr_type_name):
            data_str = XMLWrapper.getNodeText(list_node)
            data = self._attributeCastToType(data_str, attr_type_name)
        else:
            if attr_type_instance == object:
                data = class_type(list_node, find_prefix)
            else:
                data = attr_type_instance(list_node, find_prefix)

        if hasattr(data, "is_empty_object"):
            return None
        else:
            return data

    def _parseAttributesData(self, class_type, xml_object, find_prefix):
        attrib_data_dict = dict()

        empty_object_size = len(self.__dict__)

        for name, attr_type in self.__dict__.items():
            if not isinstance(attr_type, type) and not isinstance(attr_type, dict):
                continue

            if not isinstance(attr_type, dict):
                data = None
                attr_type_name = attr_type.__name__
                if self._isAttributeTypeDefault(attr_type_name):
                    data_str = XMLWrapper.getNodeAttr(xml_object, name)
                    if data_str is None:
                        child_attribute = XMLWrapper.getChildNode(xml_object, name)
                        if child_attribute is not None:
                            data_str = XMLWrapper.getNodeText(child_attribute)

                    data = self._attributeCastToType(data_str, attr_type_name)
                else:
                    child_node = XMLWrapper.getChildNode(xml_object, name)

                    if child_node is None:
                        continue

                    child_type = XMLWrapper.getNodeAttr(child_node, 'type', find_prefix)
                    if child_type is None:
                        data = attr_type(child_node, find_prefix)
                    else:
                        data = child_type(child_node, find_prefix)

                attrib_data_dict[name] = data
            else:
                child_node = XMLWrapper.getChildNode(xml_object, name)

                data_list = list()
                attr_type_instance = attr_type['list']
                attr_type_name = attr_type_instance.__name__;

                if child_node is not None:
                    child_count = 0
                    for list_node in child_node:
                        data_object = self._append_object_list(attr_type_name, list_node, attr_type_instance,
                                                               class_type, find_prefix)

                        if data_object is not None:
                            data_list.append(data_object)
                            child_count += 1

                    # I think its a logical bug, but ...
                    if child_count == 0:
                        for list_node in xml_object:
                            if XMLWrapper.getNodeName(list_node) == name:
                                data_object = self._append_object_list(attr_type_name, list_node, attr_type_instance,
                                                                       class_type, find_prefix)

                                if data_object is not None:
                                    data_list.append(data_object)

                attrib_data_dict[name] = data_list

        if not self._is_empty_object(attrib_data_dict):
            for key, value in attrib_data_dict.items():
                setattr(self, key, value)
        elif len(self.__dict__) == empty_object_size:
            setattr(self, "is_empty_object", True)

    def __init__(self, xml_object, find_prefix):
        self._parseAttributesData(self.__class__, xml_object, find_prefix)


class CommonApiResult:
    def __init__(self, xml_object):
        error_node = XMLWrapper.getChildNode(xml_object, 'Error')
        self.error = None if error_node is None else XMLWrapper.getNodeText(error_node)

        error_code_node = XMLWrapper.getChildNode(xml_object, 'ErrorCode')
        self.error_code = None if error_code_node is None else XMLWrapper.getNodeText(error_code_node)

        self.response_info = None
        response_info_node = XMLWrapper.getChildNode(xml_object, 'ResponseInfo')

        if response_info_node is not None:
            find_prefix = XMLWrapper.getNodePrefix(response_info_node, 'xsi')
            type_attr = XMLWrapper.getNodeAttr(response_info_node, find_prefix + 'type')
            if not type_attr is None:
                response_class = CommonApiResult.importAPIClass(type_attr)
                if response_class is not None:
                    self.response_info = response_class(response_info_node, find_prefix)

        success = XMLWrapper.getNodeAttr(xml_object, 'Success')
        success = success.lower()

        self.success = success in ['true', 'yes', 'on']

    @staticmethod
    def importAPIClass(name):
        module = importlib.import_module('lib.cloudshell.api.cloudshell_api')
        if hasattr(module, name):
            return getattr(module, name)

        return None


class CloudShellAPIError(Exception):
    def __init__(self, code, message, rawxml):
        self.code = code
        self.message = message
        self.rawxml = rawxml

    def __str__(self):
        return 'CloudShell API error ' + str(self.code) + ': ' + self.message

    def __repr__(self):
        return 'CloudShell API error ' + str(self.code) + ': ' + self.message


class CommonAPISession:
    def __init__(self, host, username, password, domain):
        self.host = host
        self.username = username
        self.password = password
        self.domain = domain

    def _parseXML(self, xml_str):
        return etree.fromstring(xml_str)

    def _replaceSendValue(self, data):
        """Normalize xml string, escape special xml characters
        """
        if data is None: return u''

        try:
            data_str = str(data)
        except:
            data_str = str(data.decode("utf-8"))

        data_str = u"".join([escape(char) for char in data_str])

        if data_str == 'True' or data_str == 'False':
            return data_str.lower()
        else:
            return data_str

    def _to_unicode_string(self, data):
        if data is None:
            return u''
        try:
            return str(data)
        except:
            return str(data.decode("utf-8"))

    def _encodeHeaders(self):
        self.headers = dict((key.encode('ascii') if isinstance(key, str) else key,
                             value.encode('ascii') if isinstance(value, str) else value)
                            for key, value in self.headers.items())

    def _sendRequest(self, operation, message, request_headers):
        """
        Sending http POST request through URLLIB package

        :param operation: operation name
        :param message: request body
        :param request_headers: header of the request

        :return: responce string data
        """
        operation_url = str(self.url + operation)
        parse_results = urlparse(operation_url)

        connection = http_client.HTTPConnection(parse_results.netloc)
        connection.request(method="POST",
                           url=parse_results.path,
                           headers=request_headers,
                           body=message)

        response = connection.getresponse()
        return_value = response.read()

        return return_value

    # THE METHOD TO DELETE
    def _serializeRequestData(self, object_data, prev_type=None):
        """Deprecated method which generated xml request using string concatenation, replaced with _new_serializeRequestData
        """
        request_str = ''
        if isinstance(object_data, dict):
            if len(object_data) == 0:
                return request_str

            if '__name__' not in object_data:
                raise Exception('CloudShell API', "Object data doesn't have '__name__' attribute!")

            request_str += '<' + object_data['__name__'] + '>\n'
            for key, value in object_data.items():
                if value is None or key == '__name__':
                    continue
                request_str += '<' + key + '>' + self._serializeRequestData(value) + '</' + key + '>\n'
            request_str += '</' + object_data['__name__'] + '>\n'
        elif isinstance(object_data, list):
            request_str += '\n'
            for value in object_data:
                request_str += self._serializeRequestData(value, list())
        elif isinstance(object_data, str) or isinstance(object_data, int) or isinstance(object_data, float):
            if prev_type is not None and isinstance(prev_type, list):
                request_str += '<string>' + self._replaceSendValue(str(object_data)) + '</string>\n'
            else:
                request_str += self._replaceSendValue(str(object_data))

        return request_str

    def _new_serializeRequestData(self, root_node, object_data, prev_type=None):
        """Generate xml from received request data using etree.xml
        """

        if isinstance(object_data, dict):
            if '__name__' in object_data:
                working_node = etree.SubElement(root_node, object_data.pop('__name__'))
            else:
                working_node = root_node

            for key, value in object_data.items():
                if value is None:
                    continue

                if isinstance(value, str):
                    new_node = etree.SubElement(working_node, key)
                    new_node.text = value

                else:
                    child_node = working_node
                    if (isinstance(value, list)):
                        child_node = etree.SubElement(working_node, key)
                    serialized_node = self._new_serializeRequestData(child_node, value)
            return root_node

        elif isinstance(object_data, list):
            for value in object_data:
                serialized_node = self._new_serializeRequestData(root_node, value, list())

        elif isinstance(object_data, str) or isinstance(object_data, int) or isinstance(object_data, float):
            if prev_type is not None and isinstance(prev_type, list):
                child_node = etree.SubElement(root_node, 'string')
                child_node.text = object_data
            elif isinstance(object_data, bool):
                root_node.text = str(object_data).lower()
            else:
                root_node.text = self._to_unicode_string(object_data)

        return root_node

    def generateAPIRequest(self, kwargs):
        """
        Generic method for generation and sending XML requests

        :param return_type: type of returning data
        :param kwargs: map of the parameters that need to be send to the server

        :return: string data or API object
        """

        if 'method_name' not in kwargs:
            raise CloudShellAPIError(404, 'Key "method_name" not in input data!', '')
        method_name = kwargs.pop('method_name', None)

        request_node = etree.Element(method_name)
        # request_str = '<' + method_name + '>\n'

        for name in kwargs:
            child_node = etree.SubElement(request_node, name)
            self._new_serializeRequestData(child_node, kwargs[name])

        response_str = self._sendRequest(self.username, self.domain, method_name, etree.tostring(request_node))

        response_str = response_str.replace(b'xmlns="http://schemas.qualisystems.com/ResourceManagement/ApiCommandResult.xsd" ', b'') \
            .replace(b'&#x0;', b'<NUL>')

        response_xml = XMLWrapper.parseXML(response_str)
        api_result = CommonApiResult(response_xml)

        if not api_result.success:
            raise CloudShellAPIError(api_result.error_code, api_result.error, response_str)

        if api_result.response_info is None:
            return response_str
        else:
            return api_result.response_info

    def __prettify_xml(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        from xml.dom.minidom import parse, parseString
        rough_string = etree.tostring(elem, 'utf-8')
        reparsed = parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
