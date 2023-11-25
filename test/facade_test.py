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

def test_facade():
    client = FTPClientFacade()
    client.run()
    print(test_connect(client))
    print(test_get_data(client))
    print(test_set_local_dir(client))
    print(test_send_file_default(client))
    print(test_delete(client))
    # test_get_file()
    # test_send_file_default_append()
    # Test change dir
    test_disconnect(client)
    client.close()
    return


test_facade()