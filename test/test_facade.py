from client import FTPClientFacade
import os
import time
import unittest


def test_connect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.login(callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_login(client, username='user', password='pass'):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.login(username=username, password=password, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_get_data(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.get_initial_data(callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    result = responses[0]
    if not result[0]:
        return False
    return True

def test_disconnect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.logout(callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_send_file(client, mode):
    src_path = 'send_text.txt'
    dest_path = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    client.upload_file(src_path, dest_path, mode, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_send_file_default(client):
    mode = 'w'
    return test_send_file(client, mode)
    
def test_send_file_append(client):
    mode = 'a'
    return test_send_file(client, mode)

def test_set_local_dir(client):
    test_dir = os.path.abspath("data")
    responses = []
    def set_responses(response):
        responses.append(response)
    client.set_local_dir(test_dir, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_set_remote_dir(client):
    test_dir = "subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.set_remote_dir(test_dir, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_delete(client):
    test_file = 'renamed_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    client.delete_file(test_file, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_retrieve_file(client):
    src_path = 'send_text.txt'
    dest_path = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    client.download_file(src_path, dest_path, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_rename_remote_file(client):
    old_name = 'send_text.txt'
    new_name = 'renamed_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    client.rename_remote_file(old_name, new_name, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_make_remote_dir(client):
    test_dir = "test_subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.make_remote_dir(test_dir, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False

def test_delete_remote_dir(client):
    test_dir = "test_subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.delete_remote_dir(test_dir, callback=set_responses)
    for i in range(100):
        time.sleep(0.1)
        if responses: break
    if responses.pop()[0]:
        return True
    return False
class TestFTPClientFacade(unittest.TestCase):
    def setUp(self):
        self.client = FTPClientFacade()
        self.client.run()
    
    def tearDown(self):
        self.client.close()
    
    def test_login(self):
        self.assertTrue(test_login(self.client),'Login failed')
        print('Login                PASSED')

    def test_facade_flow(self):
        self.assertTrue(test_connect(self.client),'Connect failed')
        print('Anon login           PASSED')
        self.assertTrue(test_get_data(self.client),'Get data failed')
        print('Get data             PASSED')
        self.assertTrue(test_set_local_dir(self.client),'Set local dir failed')
        print('Set local dir        PASSED')
        self.assertTrue(test_set_remote_dir(self.client),'Set remote dir failed.')
        print('Set remote dir       PASSED')
        self.assertTrue(test_make_remote_dir(self.client),'Make remote dir failed.')
        print('Make remote dir      PASSED')
        self.assertTrue(test_send_file_default(self.client),'Store file failed.')
        print('Store file           PASSED')
        self.assertTrue(test_send_file_append(self.client),'Append file failed.')
        print('Append file          PASSED')
        self.assertTrue(test_retrieve_file(self.client),'Retrieve file failed.')
        print('Retrieve file        PASSED')
        self.assertTrue(test_rename_remote_file(self.client),'Rename remote file failed.')
        print('Rename remote file   PASSED')
        self.assertTrue(test_delete(self.client),'Delete file failed.')
        print('Delete file          PASSED')
        self.assertTrue(test_delete_remote_dir(self.client),'Remove remote dir failed.')
        print('Remove remote dir    PASSED')
        self.assertTrue(test_disconnect(self.client),'Disconnect failed.')
        print('Disconnect           PASSED')