from client import FTPClientFacade
import os
import time

def test_connect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    def default_login():
        client.login(callback=set_responses)
    client.enqueue(default_login)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_get_data(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    def get_initial_data():
        client.get_initial_data(callback=set_responses)
    client.enqueue(get_initial_data)
    while not responses:
        time.sleep(0.1)
    result = responses[0]
    if result[0] == '' or not result[1] or result[2] == '':
        return False
    return True

def test_disconnect(client):
    responses = []
    def set_responses(response):
        responses.append(response)
    def default_logout():
        client.logout(callback=set_responses)
    client.enqueue(default_logout)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_send_file(client, mode):
    src_path = 'send_text.txt'
    dest_path = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    def send_file():
        client.upload_file(src_path, dest_path, mode, callback=set_responses)
    client.enqueue(send_file)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_send_file_default(client):
    mode = 'w'
    test_send_file(client, mode)
    
def test_send_file_append(client):
    mode = 'a'
    test_send_file(client, mode)

def test_set_local_dir(client):
    test_dir = "C:\\Users\\starp\\Documents\\SJSU\\cmpe148\\FTP\\test\\data"
    responses = []
    def set_responses(response):
        responses.append(response)
    def set_local_dir():
        client.set_local_dir(test_dir, callback=set_responses)
    client.enqueue(set_local_dir)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_set_remote_dir(client):
    test_dir = "subfolder/"
    responses = []
    def set_responses(response):
        responses.append(response)
    def set_remote_dir():
        client.set_remote_dir(test_dir, callback=set_responses)
    client.enqueue(set_remote_dir)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_delete(client):
    test_file = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    def delete_file():
        client.delete_file(test_file, callback=set_responses)
    client.enqueue(delete_file)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_retrieve_file(client):
    src_path = 'send_text.txt'
    dest_path = 'send_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    def retrieve_file():
        client.download_file(src_path, dest_path, callback=set_responses)
    client.enqueue(retrieve_file)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_rename_remote_file(client):
    old_name = 'send_text.txt'
    new_name = 'renamed_text.txt'
    responses = []
    def set_responses(response):
        responses.append(response)
    def rename_file():
        client.rename_remote_file(old_name, new_name, callback=set_responses)
    client.enqueue(rename_file)
    while not responses:
        time.sleep(0.1)
    if responses.pop():
        return True
    return False

def test_facade():
    client = FTPClientFacade()
    client.run()
    print(f'Test: connect         Result: {test_connect(client)}')
    print(f'Test: data            Result: {test_get_data(client)}')
    print(f'Test: set local dir   Result: {test_set_local_dir(client)}')
    print(f'Test: set remote dir  Result: {test_set_remote_dir(client)}')
    print(f'Test: stor            Result: {test_send_file_default(client)}')
    print(f'Test: append          Result: {test_send_file_append(client)}')
    print(f'Test: retrieve        Result: {test_retrieve_file(client)}')
    print(f'Test: rename remote   Result: {test_rename_remote_file(client)}')
    # print(f'Test: delete          Result: {test_delete(client)}')

    print(f'Test: disconnect.     Result: {test_disconnect(client)}')
    client.close()
    return


test_facade()