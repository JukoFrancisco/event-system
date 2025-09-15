import requests

server_url = 'http://127.0.0.1:5000'

def create_event(event_name, event_date):
    event = {'name': event_name, 'date': event_date}
    response = requests.post(f'{server_url}/events', json=event)
    print(response.json())

def list_events():
    response = requests.get(f'{server_url}/events')
    events = response.json()
    print('Events:')
    for i, event in enumerate(events):
        print(f'{i}: {event["name"]} on {event["date"]}')

def register_student(event_id, student_name):
    student = {'name': student_name}
    response = requests.post(f'{server_url}/events/{event_id}/register', json=student)
    print(response.json())

if __name__ == '__main__':
    create_event('Hackathon', '2024-09-15')
    create_event('Science Fair', '2024-10-20')
    list_events()
    register_student(0, 'Alice')
    register_student(1, 'Bob')

