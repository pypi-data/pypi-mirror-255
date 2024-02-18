"""
MIT License
 
Copyright (c) [2024] [Anand Vishwakarma]
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import base64
import ipaddress
import os
import ssl
import psutil
import requests
import json
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from datetime import datetime
import logging
import sys
from requests.adapters import HTTPAdapter

class ArconSDK:
    SdkAppType = "C# SDK"
    SdkKey = "ngDtBlYyUF2hzPg+Xpa4uylRYagbDCXuHzlMEkHRZ1A="
    SdkIV = "c02WQmDE2HI/YKVtGiXIIg=="

    class HttpRequestDetails:
        def __init__(self):
            self.ID = 0
            self.url = ''
            self.userName = ''
            self.ARC_XWD = ''
            self.methodName = ''
            self.methodType = ''
            self.contenttype = ''
            self.postData = ''
            self.token = ''
            self.port = ''
            self.response = ''

    class NIntFileContent:
        def __init__(self):
            self.AppUsername = ''
            self.AppType = ''
            self.AppName = ''
            self.EncXWD = ''
            self.IP_MAC = []
            self.InfoEncKey = ''
            self.gatewayURL = ''
    logging.basicConfig(level=logging.INFO, filename="ArconSDK.log",filemode="a")
    def __init__(self, TokenFilePath):
        self.sdkTokenFilePath = TokenFilePath
        self.sdkIsVerified = False
        self.bearerToken = ""
        self.bearerValid = None
        self.sdkAppName = ""
        self.gatewayURL = ""
        self.digitalVaultUser = {}
       
        try:
            with open(TokenFilePath, 'r') as file:
                ni_fileContent_str = file.readline()
                
            if self.verify_content(ni_fileContent_str):
                print("ArconSDK object created.")
                logging.info("ArconSDK object created.")
                self.sdkIsVerified = True
                self.client = self.HttpRequestDetails()
                self.client.url = self.digitalVaultUser["GatewayUrl"]
            else:
                print("Download the correct file.")
                logging.warning("Download the correct file")
                self.dispose()
                raise Exception("Download the correct file.")
        except Exception as ex:
            # print("Failed to create object")
            # print(f"Exception: {str(ex)}")
            logging.error(f"Failed to create object: {str(ex)}")
            self.dispose()
            self.digitalVaultUser = {}
            raise Exception("Download the correct file.")

    def dispose(self):
        self.digitalVaultUser = {}
        self.bearerToken = ""
        self.sdkIsVerified = False
        print("Class was Disposed.")
        logging.warning("Class was Disposed")

    def verify_content(self, ni_fileContent_str):
        try:
            ni_fileContent_str = self.decrypt_content(True, ni_fileContent_str)
            self.digitalVaultUser = json.loads(ni_fileContent_str)

            if self.digitalVaultUser["AppType"].lower() != self.SdkAppType.lower():
                # print("AppType Name is Not Matched")
                logging.warning("AppType Name is Not Matched")
                return False

            appfile = __file__  # Change this line accordingly
            self.sdkAppName = os.path.splitext(os.path.basename(appfile))[0]

            if self.digitalVaultUser["AppName"].lower() != self.sdkAppName.lower():
                # print("AppName Is Not Matched")
                logging.warning("AppName Is Not Matched")
                return False

            is_valid_ip_mac = self.verify_ip_mac(self.digitalVaultUser["IP_MAC"])

            # if not is_valid_ip_mac:
            #     # print("Failed to verify IP and MAC")
            #     logging.warning("Failed to verify IP and MAC")
            #     return False

        except Exception as ex:
            self.digitalVaultUser = {}
            # print("Failed To Verify Content")
            # print(f"Exception: {str(ex)}")
            logging.error(f"Failed To Verify Content: {str(ex)}")
            return False

        return True

    def is_ip_address_in_range(self, ip_address, network_address, prefix_length):
        if ip_address.version != network_address.version:
            return False

        ip_bytes = ip_address.packed
        network_bytes = network_address.packed
        num_full_bytes = prefix_length // 8
        remaining_bits = prefix_length % 8

        for i in range(num_full_bytes):
            if ip_bytes[i] != network_bytes[i]:
                return False

        if remaining_bits > 0:
            mask = 0xFF00 >> remaining_bits
            if (ip_bytes[num_full_bytes] & mask) != (network_bytes[num_full_bytes] & mask):
                return False

        return True

    def verify_ip_mac(self, ip_mac_list):
        for network_interface in psutil.net_if_addrs():
            for ip_info in psutil.net_if_addrs()[network_interface]:
                for entry in ip_mac_list:
                    if not entry:
                        return True

                    ip_address = entry[0]
                    if '/' in entry[0] and entry[1] == "0":
                        parts = entry[0].split('/')
                        prefix_length = int(parts[1])
                        network_address = ipaddress.IPv4Address(parts[0])
                        if self.is_ip_address_in_range(ip_info.address, network_address, prefix_length):
                            return True

                    if ip_info.address == ip_address:
                        mac_address = entry[1]
                        if mac_address == "0":
                            return True
                        else:
                            mac_address = mac_address.replace("-", "")
                            physical_address = psutil.net_if_addrs()[network_interface][1].address
                            if physical_address.lower() == mac_address.lower():
                                return True
                            else:
                                return False

        return False

    
    def encrypt_content(self,is_fk, content, key=""):
        sdk_key = ""
        sdk_iv = ""

        if is_fk:
            key = base64.b64decode(self.SdkKey)
            iv = base64.b64decode(self.SdkIV)
        else:
            key = base64.b64decode(key)
            iv = base64.b64decode(self.SdkIV)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the content to be a multiple of 16 bytes
        content_padded = content + (16 - len(content) % 16) * chr(16 - len(content) % 16)

        encrypted_bytes = cipher.encrypt(content_padded.encode('utf-8'))
        enc_str = base64.b64encode(encrypted_bytes).decode('utf-8')

        return enc_str

 
    def decrypt_content(self,is_fk, content, key=""):
        
        sdk_iv=""
        if is_fk:
            key = base64.b64decode(self.SdkKey)
            iv = base64.b64decode(self.SdkIV)
        else:
            key = base64.b64decode(key)
            iv = base64.b64decode(self.SdkIV)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        encrypted_bytes = base64.b64decode(content)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)

        # Unpad the decrypted content
        dec_str = decrypted_bytes[:-decrypted_bytes[-1]].decode('utf-8')

        return dec_str


    def cert_validation(self, server_url, development):
        if server_url.upper().startswith("HTTPS"):
            session = requests.Session()
            session.mount(server_url, HTTPAdapter())
            if development:
                session.verify = False

    def create_http_request(self, obj_http_request_details, is_token=False):
            server_url = obj_http_request_details.url + "/" + obj_http_request_details.methodName
            server_url = re.sub(r'(https?://[^/]+)//*', r'\1/', server_url)

            headers = {
                'Content-Type': obj_http_request_details.contenttype,
                'Accept': obj_http_request_details.contenttype
            }

            if obj_http_request_details.token:
                headers['Authorization'] = f"Bearer {obj_http_request_details.token}"

            if not is_token:
                headers['ArcSecResBody'] = '1'
                headers['AppUserName'] = base64.b64encode(self.encrypt_content(True, self.digitalVaultUser["AppUsername"]).encode()).decode('utf-8')
                headers['AppTypeName'] = base64.b64encode(self.digitalVaultUser["AppType"].encode()).decode('utf-8')
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # To work with older SSL/TLS versions
            ssl_context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
            self.cert_validation(server_url,True)
            data = obj_http_request_details.postData
            request = requests.Request("POST", server_url, data=data, headers=headers)
            # response = requests.post(server_url, headers=headers, data=data, verify=False)
            return request
    def response_post_data(self, request):
        data = ''
        try:
            # response = requests.post(request.url)
            response = requests.post(request.url,data = request.data,headers=request.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.text
        except requests.exceptions.HTTPError as http_err:
                if http_err.response is not None:
                    if http_err.response.status_code == 401:  # Unauthorized
                        data = "Error: Authentication failed"
                    elif http_err.response.status_code == 400:  # Bad Request
                        data = f"Error: Bad Request {http_err}"
                    else:
                        data = f"Error: {http_err}"
                        print("THE ERROR IS ",data)
                else:
                    data = f"Error: {http_err}"
        except Exception as e:
                data = f"Error: {e}"
                print("The data is ",data)
        return data

    def get_bearer_token(self):
        self.bearerToken = ''
        bearer_client = self.HttpRequestDetails()
        bearer_client.url = self.digitalVaultUser["GatewayUrl"]
        bearer_client.methodName = '/Auth/api/Token/GetTokenByKey'
        bearer_client.methodType = 'POST'
        bearer_client.contenttype = 'application/json'

        app_key = json.dumps({
            "EncXWD": self.digitalVaultUser["EncXWD"],
            "AppName": self.digitalVaultUser["AppName"]
        })

        bearer_client.postData = json.dumps({
            "AppUserName": self.encrypt_content(True, self.digitalVaultUser["AppUsername"]),
            "AppTypeName": "C# SDK",
            "AppKey": self.encrypt_content(False, app_key, self.digitalVaultUser["InfoEncKey"])
        })

        bearer_api_response = self.response_post_data(self.create_http_request(bearer_client, True))
        is_resp_success = json.loads(bearer_api_response).get("success", False)

        if not is_resp_success or not bearer_api_response:
            self.bearerToken = ''
        else:
            self.bearerToken = json.loads(bearer_api_response).get("accessToken", "")
            self.bearerValid = json.loads(bearer_api_response).get("expiresIn", "")
            # self.bearerValid = datetime.strptime(expires_in_str, "%Y-%m-%dT%H:%M:%S")

        self.client.token = self.bearerToken

    def get_credential(self, api_method_type, api_content_type, post_data=""):
        method_name = '/Vault/api/vault/GetTargetDevicePassKey'
        method_type = api_method_type
        content_type = ""

        try:
            if api_content_type == "JSON":
                content_type = "application/json"
            elif api_content_type == "XML":
                content_type = "application/xml"

            # print("API request made:")
            logging.info("API request made:")
            if self.bearerValid is None or self.bearerValid < datetime.now():
                self.get_bearer_token()
        except Exception as ex:
            print("Error at get_credential")
            print(f"Exception: {str(ex)}")
            self.digitalVaultUser = {}
            logging.error(f"Error at get_credential Exception: {str(ex)}")
            return ""

        try:
            if method_type.upper() == "GET":
                self.client.methodName = method_name
                self.client.methodType = "GET"
                self.client.contenttype = content_type
                pam_api_response = self.response_post_data(self.create_http_request(self.client))
            elif method_type.upper() == "POST":
                self.client.methodName = method_name
                self.client.postData = post_data
                self.client.methodType = "POST"
                self.client.contenttype = content_type
                pam_api_response = self.response_post_data(self.create_http_request(self.client))
            else:
                raise NotImplementedError()

            is_resp_success = json.loads(pam_api_response).get("Message") == "Success"

            if not is_resp_success or not pam_api_response:
                # print("Error at get_credential")
                logging.warning("Error at get_credential")
                self.digitalVaultUser = {}
                return ""
            else:
                pam_api_response_json = json.loads(pam_api_response)
                service_details_decrypt = pam_api_response_json.get("Result", "")
                service_details_decrypt = self.decrypt_content(False, service_details_decrypt,self.digitalVaultUser["InfoEncKey"])
                pam_api_response = service_details_decrypt
                
            return pam_api_response
        except Exception as ex:
            print("Error at get_credential")
            print(f"Exception: {str(ex)}")
            self.digitalVaultUser = {}
            logging.error(f"Error at get_credential Exception: {str(ex)}")
            return ""

    def main(self, api_method_type, api_content_type, post_data):
        response = self.get_credential(api_method_type, api_content_type, post_data)
        print(response)

if __name__ == "__main__":
    _instance = ArconSDK(sys.argv[1])  # Only initialize once with the correct argument
    _instance.main(sys.argv[2], sys.argv[3], sys.argv[4])  # Pass the correct arguments for API usage


#     _instance=ArconSDK(sys.argv[1])
#     y=_instance.get_credential(sys.argv[2],sys.argv[3],sys.argv[4])
#     print(y)
    