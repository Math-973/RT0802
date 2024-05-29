from flask import Flask, request, jsonify
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key
import datetime
import os
import logging
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# Configurer la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Charger le certificat et la clé de la CA
with open("certs/ca_cert.pem", "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(f.read())

with open("certs/ca_key.pem", "rb") as f:
    ca_key = load_pem_private_key(f.read(), password=None)

# Liste des certificats révoqués
revoked_certs = set()

MQTT_BROKER = "194.57.103.203"
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle"

def sign_csr(csr):
    cert = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    ).sign(ca_key, hashes.SHA256())
    
    return cert

@app.route('/sign-csr', methods=['POST'])
def sign_csr_endpoint():
    csr = x509.load_pem_x509_csr(request.data)
    signed_cert = sign_csr(csr)
    logging.info("CSR reçu et signé pour : %s", csr.subject)
    return signed_cert.public_bytes(Encoding.PEM)

@app.route('/revoke-cert', methods=['POST'])
def revoke_cert():
    serial_number = int(request.json['serial_number'])
    revoked_certs.add(serial_number)
    logging.info("Certificat révoqué: %s", serial_number)
    return jsonify({"status": "success", "serial_number": serial_number})

@app.route('/is-revoked', methods=['POST'])
def is_revoked():
    cert_pem = request.data
    cert = x509.load_pem_x509_certificate(cert_pem)
    serial_number = cert.serial_number
    is_revoked = serial_number in revoked_certs
    logging.info("Vérification de la révocation pour le certificat %s: %s", serial_number, is_revoked)
    return jsonify({"revoked": is_revoked})

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code %s", str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload)
        if 'action' in message and message['action'] == 'verify':
            cert_pem = message['certificate'].encode()
            cert = x509.load_pem_x509_certificate(cert_pem)
            serial_number = cert.serial_number
            is_revoked = serial_number in revoked_certs
            response = {"vendor": message['vendor'], "revoked": is_revoked}
            client.publish(MQTT_TOPIC, json.dumps(response))
            logging.info("Vérification de la révocation pour le certificat %s: %s", serial_number, is_revoked)
    except Exception as e:
        logging.error("Error processing message: %s", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

if __name__ == '__main__':
    app.run(port=5000)