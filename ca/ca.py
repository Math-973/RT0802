from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import datetime
import os

# Crée le répertoire pour stocker les certificats s'il n'existe pas
os.makedirs("certs", exist_ok=True)

# Générer la clé privée pour la CA
ca_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Détails du certificat de la CA
ca_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Some-State"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Locality"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CA Organization"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"My CA"),
])

# Construire le certificat auto-signé de la CA
ca_cert = x509.CertificateBuilder().subject_name(
    ca_subject
).issuer_name(
    ca_subject
).public_key(
    ca_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Le certificat sera valide pour 10 ans
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.BasicConstraints(ca=True, path_length=None), critical=True,
).sign(ca_key, hashes.SHA256())

# Sauvegarder la clé privée de la CA
with open("certs/ca_key.pem", "wb") as f:
    f.write(ca_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption()
    ))

# Sauvegarder le certificat auto-signé de la CA
with open("certs/ca_cert.pem", "wb") as f:
    f.write(ca_cert.public_bytes(Encoding.PEM))

print("CA key and certificate have been generated and saved.")