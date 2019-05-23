#!usr/bin/python3
import argparse
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError
import paho.mqtt.client as mqtt

# Connection details
# We will use these settings later in the code to connect to the
# RethinkDB server.
RDB_HOST = 'localhost'
RDB_PORT = 28015
MQTT_DB = 'mqttdata'
r = rdb.RethinkDB()
topics = list() # stores all topic names


def dbSetup():
    '''Setting up the app database
    The app will use a table `topics` in the database specified by the MQTT_DB
    variable.  We'll create the database and table here using db_create and
    table_create commands.'''
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(MQTT_DB).run(connection)
        r.db(MQTT_DB).table_create('data').run(connection)
        r.db(MQTT_DB).table_create('topics').run(connection)
        r.db(MQTT_DB).table_create('users').run(connection)
        # Create a secondary index on the topic name attribute
        r.table("topics").index_create("name").run(connection)
        # Create a secondary index on the data topic_id attribute
        r.table("data").index_create("topic_id").run(connection)
        r.table("data").index_create("timestamp").run(connection)

        r.table("topics").index_wait("name").run(connection)
        r.table("data").index_wait("topic_id").run(connection)
        print ('Database setup completed. Now run the app without --setup.')
    except RqlRuntimeError:
        print ('Api database already exists. Run the app without --setup.')
    finally:
        connection.close()


def on_connect(client, userdata, flags, rc):
    '''The callback for when the client receives a CONNACK response from the
    server. Client subscribe to all topics on broker.
    list of topics is populated'''
    print("Connected with result code "+str(rc))
    client.subscribe("#")
    global topics
    connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=MQTT_DB)
    topics = list(r.table('topics').get_field('name').run(connection))


def on_message(client, userdata, msg):
    '''The callback for when a PUBLISH message is received from the server.
    messages are saved to rethinkdb. '''
    global topics
    connection = r.connect(host=RDB_HOST, port=RDB_PORT, db=MQTT_DB)
    print("Recived data topic:" + msg.topic+", value: "+str(msg.payload))
    try:
        # check if topic already exists
        if msg.topic not in topics:
            # topic not in database: insert topic
            topic_id = r.table('topics').insert({
                "name": msg.topic,
                "user_id": "notSet",
                })['generated_keys'][0].run(connection)
            topics.append(msg.topic)
            print(topic_id)
            print("new topic added")
        else:
            # topic allready in database: get it's id
            topic_id = r.table('topics').get_all(msg.topic, index='name')['id'][0].run(connection)
        # insert data
        r.table('data').insert({
            "timestamp": r.now(),
            "data": str(msg.payload),
            "topic_id": topic_id,
            }).run(connection)
        print ("new data added!")

    except RqlRuntimeError as err:
        print("exception: " + err.message)
    finally:
        connection.close()


def run():
    ''' main mqtt client loop
    '''
    client = mqtt.Client(client_id="MQTT rethinkDB bridge")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username="myuser", password="mypass")
    client.connect("127.0.0.1", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run MQTT rethinkDB bridge')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        run()
