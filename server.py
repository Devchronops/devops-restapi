import os
import redis, fakeredis
from flask import Flask, Response, jsonify, request, json

app = Flask(__name__)
app.debug = True
# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

users = {"0":{"name": "Carlos Guzman", "times":[{"from":1477523957, "to":1477524957}]}}

@app.route('/')
def index():
    # docs = {
    #   "name": "Meeting REST API",
    #   "version": "1.0",
    #   "domain": "http://devchronops.mybluemix.net",
    #   "url": [
    #     {
    #       "url":"/users",
    #       "method": "GET",
    #       "description": "List all users"
    #     },{
    #       "url":"/users/<id>",
    #       "method": "GET",
    #       "description": "Get user with id <id>"
    #     },{
    #       "url":"/meet?users=<id1>,<id2>",
    #       "method": "GET",
    #       "description": "Get possible meeting times for users <id1>, <id2>.... specified by comma-separated values"
    #     },{
    #       "url":"/users",
    #       "method": "POST",
    #       "description": "Create a user",
    #       "sample_body": {
    #         "id": 0,
    #         "name": "John Rofrano",
    #         "times": [
    #           {
    #             "from":1477523957,
    #             "to":1477524957
    #           }
    #         ]
    #       }
    #     },{
    #       "url":"/users/<id>/times",
    #       "method": "POST",
    #       "description": "Add a time interval for user with id <id>",
    #       "sample_body": {
    #         "from":1477523957,
    #         "to":1477524957
    #       }
    #     },{
    #       "url":"/users/<id>",
    #       "method": "DELETE",
    #       "description": "Delete a user"
    #     },{
    #       "url":"/users/<id>/times",
    #       "method": "PUT",
    #       "description": "Delete time interval specified for user with id <id>",
    #       "sample_body": {
    #         "from":1477523967,
    #         "to":1477524958
    #       }     
    #     },{
    #       "url":"/users/<id>",
    #       "method": "PUT",
    #       "description": "Update user with id <id>. Updates name and times",
    #       "sample_body": {
    #         "name": "JR",
    #         "times": [
    #           {
    #             "from":1477523967,
    #             "to":1477524958
    #           },{
    #             "from":14772396000,
    #             "to":  147752490000
    #           }
    #         ]
    #       }     
    #     }
    #   ]
    # }
    # return reply(docs, HTTP_200_OK)
    """Sends the Swagger main HTML page to the client.
        Returns:
            response (Response): HTML content of static/swagger/index.html
    """
    return app.send_static_file('swagger/index.html')   

@app.route('/lib/<path:path>')
def send_lib(path):

    return app.send_static_file('swagger/lib/' + path)

@app.route('/specification/<path:path>')
def send_specification(path):

    return app.send_static_file('swagger/specification/' + path)

@app.route('/images/<path:path>')
def send_images(path):

    return app.send_static_file('swagger/images/' + path)

@app.route('/css/<path:path>')
def send_css(path):

    return app.send_static_file('swagger/css/' + path)

@app.route('/fonts/<path:path>')
def send_fonts(path):

    return app.send_static_file('swagger/fonts/' + path)


@app.route('/users/<id>', methods=['DELETE'])
def delete_users(id):
    global users
    users = get_from_redis('users')
    if not users.has_key(id):
        return reply({ 'error' : 'User %s doesn\'t exist' % id }, HTTP_400_BAD_REQUEST)
    del users[id];
    json_users=json.dumps(users)
    redis_server.set('users',json_users)
    return reply('', HTTP_204_NO_CONTENT)

@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    global users
    users = get_from_redis('users')
    payload = json.loads(request.data)
    if users.has_key(id):
        users[id] = {'name': payload['name'], 'times': payload['times']}
        json_users=json.dumps(users)
        redis_server.set('users',json_users)
        message = users[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'User %s was not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

@app.route('/users', methods=['GET'])
def list_users():
    global users
    users = get_from_redis('users')
    return reply(users, HTTP_200_OK)


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    global users
    users = get_from_redis('users')
    if not users.has_key(id):
        return reply({'error' : 'User %s doesn\'t exist' % id}, HTTP_400_BAD_REQUEST)
    return reply(users[id], HTTP_200_OK)


@app.route('/users', methods=['POST'])
def create_user():
    global users
    payload = json.loads(request.data)
    users = get_from_redis('users')
    id = len(users) + 1
    if users.has_key(id):
        message = { 'error' : 'User %s already exists' % id }
        rc = HTTP_409_CONFLICT
    else:
        users[id] = payload
        message = users[id]
        rc = HTTP_201_CREATED
        json_users=json.dumps(users)
        redis_server.set('users',json_users)
    return reply(message, rc)

@app.route('/users/<id>/times', methods=['POST'])
def set_times(id):
    global users
    payload = json.loads(request.data)
    users = get_from_redis('users')
    if not users.has_key(id):
        return reply({'error' : 'User %s doesn\'t exist' % id}, HTTP_400_BAD_REQUEST)
    if not payload.has_key('from') or not payload.has_key('to') \
        and type(payload['from']) == int and type(payload['to']) == int:
        return reply({'error' : 'Body must be an object with "from" and "to" being integer fields'}, HTTP_400_BAD_REQUEST)
    
    # print(users['2'])
    users[id]['times'].append(payload)
    json_users=json.dumps(users)
    redis_server.set('users',json_users)
    return reply(users[id], HTTP_200_OK)

@app.route('/users/<id>/times', methods=['PUT'])
def remove_times(id):
    global users
    payload = json.loads(request.data)
    users = get_from_redis('users')
    if not users.has_key(id):
        return reply({'error' : 'User %s doesn\'t exist' % id}, HTTP_400_BAD_REQUEST)
    if not payload.has_key('from') or not payload.has_key('to') \
        and type(payload['from']) == int and type(payload['to']) == int:
        return reply({'error' : 'Body must be an object with "from" and "to" being integer fields'}, HTTP_400_BAD_REQUEST)
    ndx = None
    for i in range(len(users[id]['times'])):
        if users[id]['times'][i]['from'] == payload['from'] \
            and users[id]['times'][i]['to'] == payload['to']:
            ndx = i
            break
    if ndx is not None:
        del users[id]['times'][ndx]
        json_users = json.dumps(users)
        redis_server.set('users', json_users)
        return reply(users[id], HTTP_200_OK)
    else:
        return reply({'error' : 'Body must already be within the timeslots'}, HTTP_400_BAD_REQUEST)

@app.route('/meet', methods=['GET'])
def meet():
    global users
    users = json.loads(redis_server.get('users'))
    ids = request.args.get('users').split(',')
    if any([not users.has_key(x) for x in ids]):
        return reply({ 'error' : 'Enter valid existing user ids'}, HTTP_400_BAD_REQUEST)
    single_schedules = map(lambda _id: [(x['from'], x['to'], [_id])
                                        for x in users[_id]['times']],
                            ids)
    final_schedule = reduce(merge, single_schedules)

    # Keep only the intervals greater than the duration
    duration = request.args.get('length') or 0
    final_schedule = filter(lambda x: x[1]-x[0]>= int(duration), final_schedule)
    
    # Check if there are results
    if not final_schedule:
      return reply([], HTTP_200_OK)

    # Return the times where most people can meet
    max_people = len(max(final_schedule, key=lambda x: len(x[2]))[2])
    if max_people == 1:
      return reply([], HTTP_200_OK)
    final_schedule = filter(lambda x: len(x[2])==max_people, final_schedule)
    final_schedule.sort()
    json_schedule = [{"from": x[0], "to": x[1], "people": x[2]}
                     for x in final_schedule]
    return reply(json_schedule, HTTP_200_OK)

###################################################
#                Helper Functions                 #
###################################################

def merge(sched1, sched2):
    sched1.sort()
    sched2.sort()
    final_sched = []
    processed = {}
    i1 = 0
    i2 = 0
    while i1 < len(sched1) and i2 < len(sched2):
        while i1 < len(sched1) and sched1[i1][1] < sched2[i2][0]:
            final_sched.append(sched1[i1])
            i1 += 1
        # If they don't intersect, append the rest
        if i1 == len(sched1):
            final_sched.extend(sched2[i2:])
            return final_sched

        while i2 < len(sched2) and sched2[i2][1] < sched1[i1][0]:
            final_sched.append(sched2[i2])
            i2 += 1
        # If they don't intersect, append the rest
        if i2 == len(sched2):
            final_sched.extend(sched1[i1:])
            return final_sched

        # We know they intersect
        final_sched.extend(merge2(sched1[i1], sched2[i2]))
        i1 += 1
        i2 += 1

    #Remove elements that have length 0 time
    return filter(lambda x: x[0] < x[1], final_sched)

# TODO Fix algorithm, since it doesn't work when an interval intersects with more than one intervals of the other person
# e.g.
# merge([(1, 10, [1]), (12, 14, [1])], [(5, 15, [2])])

def merge2(sched1, sched2):
    final_sched = []
    first = min(sched1, sched2)
    second = max(sched1, sched2)
    final_sched.append((first[0],
                        second[0],
                        first[2]))
    if min(first[1], second[1]) == first[1]:
    # first   |--------|
    # second       |-------|
        final_sched.append((second[0],
                            first[1],
                            sorted(second[2] + first[2])))
        final_sched.append((first[1],
                            second[1],
                            second[2]))
    else:
    # first   |--------|
    # second     |---|
       final_sched.append((second[0],
                           second[1],
                           sorted(second[2] + first[2])))
       final_sched.append((second[1],
                           first[1],
                           first[2]))
    return final_sched

def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def data_reset():
    redis_server.flushall()

# Initialize Redis
def init_redis(mock=False):
    # Connect to Redis Server
    if 'VCAP_SERVICES' in os.environ:
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        redis_creds = services['rediscloud'][0]['credentials']
        # pull out the fields we need
        redis_hostname = redis_creds['hostname']
        redis_port = int(redis_creds['port'])
        redis_password = redis_creds['password']
    else:
        redis_hostname = '127.0.0.1'
        redis_port = 6379
        redis_password = None
    global redis_server

    if mock:
        redis_server = fakeredis.FakeStrictRedis()
    else:
        redis_server = redis.Redis(host=redis_hostname, port=redis_port, password=redis_password)

    if not redis_server:
        print('*** FATAL ERROR: Could not conect to the Redis Service')
        exit(1)

def get_from_redis(s):
    unpacked = redis_server.get(s)
    if unpacked:
        return json.loads(unpacked)
    else:
        return {}

if __name__ == "__main__":
    # Get the crdentials from the Bluemix environment
    

    init_redis()
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port))
