from client import FTPClientFacade
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
        print(response)
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

def test_facade():
    client = FTPClientFacade()
    client.run()
    test_connect(client)
    test_get_data(client)
    # test_send_file()
    # test_get_file()
    # test_append_file()
    test_disconnect(client)
    client.close()
    return


test_facade()