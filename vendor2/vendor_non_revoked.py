from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import requests
import os
import logging

# Configurer la journalisation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Crée le répertoire pour stocker les certificats s'il n'existe pas
os.makedirs("certs", exist_ok=True)

def create_vendor_csr(vendor_name):
    vendor_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Some-State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Locality"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, vendor_name),
        x509.NameAttribute(NameOID.COMMON_NAME, vendor_name),
    ])).sign(vendor_key, hashes.SHA256())

    return vendor_key, csr

def send_csr_to_ca(csr):
    csr_pem = csr.public_bytes(Encoding.PEM)
    response = requests.post('http://localhost:5000/sign-csr', data=csr_pem)
    return response.content

if __name__ == "__main__":
    vendor_name = "Vendor 2"
    vendor_key, csr = create_vendor_csr(vendor_name)
    logging.info("CSR généré pour %s", vendor_name)
    
    signed_cert_pem = send_csr_to_ca(csr)
    logging.info("Certificat signé reçu pour %s", vendor_name)

    with open("certs/vendor_2_key.pem", "wb") as f:
        f.write(vendor_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        ))

    with open("certs/vendor_2_cert.pem", "wb") as f:
        f.write(signed_cert_pem)

    logging.info("%s certificate signed and saved.", vendor_name)