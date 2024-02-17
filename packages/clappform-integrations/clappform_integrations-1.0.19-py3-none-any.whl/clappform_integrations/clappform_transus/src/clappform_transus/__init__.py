"""
Clappform API Wrapper
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2022 Clappform B.V..
:license: MIT, see LICENSE for more details.
"""
__requires__ = ["requests==2.28.1", "pandas==1.5.2", "beautifulsoup4==4.12.2", "xmltodict==0.13.0"]


# Metadata
__version__ = "0.0.3"
__author__ = "Clappform B.V."
__email__ = "info@clappform.com"
__license__ = "MIT"
__doc__ = "Clappform Python API wrapper"


import requests
import base64
import logging
import xml.etree.ElementTree as ET
import re

class TransusException(Exception):
    """SOAP Exceptions Class"""

class Transus:
    def __init__(self, base_url: str, client_id: str, client_key: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_key = client_key
        
    def encode_bytes_to_base64(self, file_content):
        if not isinstance(file_content, bytes):
            raise TransusException("file_content must be in bytes.")
        return base64.b64encode(file_content).decode('utf-8')



    def generate_soap_body(self, qParams: str, **kwargs) -> str:
        additional_elements = ""
        for key, value in kwargs.items():
            additional_elements += f"<{key}>{value}</{key}>"

        body = f"""
        <soap12:Body>
        <{qParams} xmlns="https://webconnect.transus.com/">
        <ClientID>{self.client_id}</ClientID>
        <ClientKey>{self.client_key}</ClientKey>
        {additional_elements}
        </{qParams}>
        </soap12:Body>
        """
        return body

    def generate_soap_request(self, qParams: str, **kwargs) -> str:
        body = self.generate_soap_body(qParams, **kwargs)
        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">{body}</soap12:Envelope>"""
        return envelope

    def send_soap_request(self, qParams: str, *args) -> dict:
        if qParams == 'M10100':
            if len(args) != 1:
                raise TransusException("For 'M10100', exactly one argument (file content in bytes) must be provided.")
            encoded_file = self.encode_bytes_to_base64(args[0])
            soap_request = self.generate_soap_request(qParams, Message=encoded_file)

        elif qParams == 'M10300':
            if len(args) != 2:
                raise TransusException("For 'M10300', exactly two arguments are required.")
            soap_request = self.generate_soap_request(qParams, TransactionID=args[0], Status=args[1], StatusDetails="")

        elif qParams == 'M10110':
            if len(args) != 0:
                raise TransusException("For 'M10110', no arguments should be provided.")
            soap_request = self.generate_soap_request(qParams)

        else:
            raise TransusException("Invalid qParams value.")

        headers = {'Content-Type': 'application/soap+xml'}
        response = requests.post(self.base_url, headers=headers, data=soap_request)

        if response.status_code != 200:
            raise TransusException(f"Failed to retrieve data from the API. Status code: {response.status_code}")
        return self.get_details_from_response(response.text)

    def get_details_from_response(self, response_text: str) -> dict:
        try:
            root = self.get_xml_namespace_free(response_text)

            response_details = {"Message": None, "TransactionID": None, "ExitCode": None}
            for element_key in response_details:
                element = root.find('.//' + element_key)
                if element is not None:
                    response_details[element_key] = element.text
        
            # Translate ExitCode
            exit_code_messages = {
                "0": "Successful completion",
                "10": "The Client ID, Client Key or IP address is invalid",
                "20": "The access has been denied for this client",
                "30": "Invalid transaction ID",
                "90": "Restriction occurred",
                "99": "An error has occurred"
            }

            exit_code = response_details['ExitCode']
            response_details['ExitCodeMessage'] = exit_code_messages.get(exit_code, f"Unspecified error (code {exit_code})")
            return response_details
        except ET.ParseError as e:
            return {"Error": f"Invalid XML format: {e}"}

    @staticmethod
    def get_xml_namespace_free(xml_string):
        """ Remove namespaces in the XML string """
        return ET.fromstring(re.sub(' xmlns="[^"]+"', '', xml_string, count=1))