import paho.mqtt.client as mqtt
import json
import time
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
import os
import logging

# Configurer la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

MQTT_BROKER = "194.57.103.203"
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle"

# Crée le répertoire pour stocker les certificats s'il n'existe pas
os.makedirs("certs", exist_ok=True)

def load_certificate(filename):
    with open(filename, "rb") as f:
        return x509.load_pem_x509_certificate(f.read())

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code %s", str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    if 'vendor' in message and message['vendor'] == 'Vendor 2' and 'revoked' in message:
        logging.info("Verification response received: %s", message)
        print(f"Client 2 - Verification response: {message}")
        if not message['revoked']:
            purchase_message = {
                'action': 'purchase',
                'client': 'Client 2',
                'vendor': 'Vendor 2'
            }
            client.publish(MQTT_TOPIC, json.dumps(purchase_message))
            logging.info("Sent purchase request for vendor Vendor 2 by client Client 2")
        else:
            logging.info("Vendor 2's certificate is revoked. Cannot proceed with purchase.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def client_action(vendor_cert):
    # Verify the certificate
    verify_message = {
        'action': 'verify',
        'vendor': 'Vendor 2',
        'certificate': vendor_cert.public_bytes(Encoding.PEM).decode()
    }
    client.publish(MQTT_TOPIC, json.dumps(verify_message))
    logging.info("Sent verification request for vendor Vendor 2")

if __name__ == "__main__":
    vendor_cert = load_certificate("../vendor2/certs/vendor_2_cert.pem")
    client_action(vendor_cert)

    # Allow some time for the messages to be processed
    time.sleep(10)

    client.loop_stop()
    client.disconnect()