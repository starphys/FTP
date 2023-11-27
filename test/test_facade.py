from client import FTPClientFacade
import os
import time

# TODO: turn these into actual test cases for unittest
def test_connect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.login(callback=set_responses)
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_get_data(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.get_initial_data(callback=set_responses)
    while not responses:
        time.sleep(0.1)
    result = responses[0]
    if not result[0]:
        return False
    return True

def test_disconnect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    client.logout(callback=set_responses)
    while not responses:
        time.sleep(0.1)
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
    while not responses:
        time.sleep(0.1)
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
    test_dir = os.path.abspath("test/data")
    responses = []
    def set_responses(response):
        responses.append(response)
    client.set_local_dir(test_dir, callback=set_responses)
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_set_remote_dir(client):
    test_dir = "subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.set_remote_dir(test_dir, callback=set_responses)
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_delete(client):
    test_file = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    client.delete_file(test_file, callback=set_responses)
    while not responses:
        time.sleep(0.1)
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
    while not responses:
        time.sleep(0.1)
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
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_make_remote_dir(client):
    test_dir = "test_subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.make_remote_dir(test_dir, callback=set_responses)
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_delete_remote_dir(client):
    test_dir = "test_subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    client.delete_remote_dir(test_dir, callback=set_responses)
    while not responses:
        time.sleep(0.1)
    if responses.pop()[0]:
        return True
    return False

def test_facade():
    client = FTPClientFacade()
    client.run()
    print(f'Test: connect          Result: {test_connect(client)}')
    print(f'Test: data             Result: {test_get_data(client)}')
    print(f'Test: set local dir    Result: {test_set_local_dir(client)}')
    print(f'Test: set remote dir   Result: {test_set_remote_dir(client)}')
    print(f'Test: make remote dir  Result: {test_make_remote_dir(client)}')
    print(f'Test: stor             Result: {test_send_file_default(client)}')
    print(f'Test: append           Result: {test_send_file_append(client)}')
    print(f'Test: retrieve         Result: {test_retrieve_file(client)}')
    print(f'Test: rename remote    Result: {test_rename_remote_file(client)}')
    print(f'Test: delete           Result: {test_delete(client)}')
    print(f'Test: rm remote dir    Result: {test_delete_remote_dir(client)}')
    print(f'Test: disconnect.      Result: {test_disconnect(client)}')
    client.close()
    return True


test_facade()