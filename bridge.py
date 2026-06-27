import os
import json
import re
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

DEVICE = {
    "identifiers": ["openwrt-router"],
    "name": "OpenWrt Router",
    "manufacturer": "OpenWrt"
}

DISCOVERY_PREFIX = "homeassistant"
STATE_PREFIX = "openwrt"

created = set()

def sanitize(s):
    return re.sub(r'[^a-zA-Z0-9_]', '_', s)

def parse_value(payload):
    try:
        return float(payload.decode().split(":")[-1])
    except:
        return None

def make_id(topic):
    return sanitize("_".join(topic.split("/")[1:]))

def publish_discovery(client, entity_id):
    topic = f"{DISCOVERY_PREFIX}/sensor/{entity_id}/config"

    payload = {
        "name": entity_id.replace("_", " ").title(),
        "state_topic": f"{STATE_PREFIX}/{entity_id}/state",
        "unique_id": entity_id,
        "device": DEVICE
    }

    client.publish(topic, json.dumps(payload), retain=True)

def on_message(client, userdata, msg):
    value = parse_value(msg.payload)
    if value is None:
        return

    entity_id = make_id(msg.topic)

    if entity_id not in created:
        publish_discovery(client, entity_id)
        created.add(entity_id)

    client.publish(f"{STATE_PREFIX}/{entity_id}/state", value)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(MQTT_HOST, MQTT_PORT, 60)

client.subscribe("collectd/#")
client.on_message = on_message

client.loop_forever()
