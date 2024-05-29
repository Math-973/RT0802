# Projet 802 - CA simulée

## Introduction

Ce projet consiste à simuler une Autorité de Certification (CA) et la gestion de certificats pour des vendeurs et des clients en utilisant le protocole MQTT.

## Structure du Projet

- `ca/` : Contient le script pour générer les certificats de la CA et l'API Flask.
- `vendor1/` : Contient le script pour le vendeur révoqué.
- `vendor2/` : Contient le script pour le vendeur non révoqué.
- `client1/` : Contient le script pour le client 1.
- `client2/` : Contient le script pour le client 2.
- `client3/` : Contient le script pour le client 3.

## Pré-requis

- Python 3.11.9
- Les bibliothèques Python : `cryptography`, `paho-mqtt`, `requests`, `flask`

## Utilisation

### Générer les Clés et Certificats de la CA

```sh
cd ca
python ca.py
```

### Copier le Certificat de la CA vers les Répertoires des Clients

Les certificats générés par la CA doivent être copiés vers les répertoires des clients pour qu'ils puissent vérifier les certificats des vendeurs.

```sh
cp ca/certs/ca_cert.pem client1/certs/
cp ca/certs/ca_cert.pem client2/certs/
cp ca/certs/ca_cert.pem client3/certs/
```

### Démarrer l'API de la CA

L'API permet de signer les CSR des vendeurs et de gérer la révocation des certificats.

```sh
cd ca
python api.py
```

### Générer les Certificats des Vendeurs

Vendeur révoqué (Vendor1) :
```sh
cd vendor1
python vendor_revoked.py
```

Vendeur non révoqué (Vendor 2) :
```sh
cd vendor2
python vendor_non_revoked.py
```

### Exécuter les scripts des clients

Actions des Clients :
- Client 1 : Vérifie le certificat du vendeur 1 (révoqué) et effectue un achat si le certificat est valide.
- Client 2 : Vérifie le certificat du vendeur 2 (non révoqué) et effectue un achat si le certificat est valide.
- Client 3 : Vérifie le certificat du vendeur 1 (révoqué), vérifie s'il est révoqué et effectue un achat uniquement si le certificat n'est pas révoqué.

Client 1 :
```sh
cd client1
python client1.py
```

Client 2 :
```sh
cd client2
python client2.py
```

Client 3 :
```sh
cd client3
python client3.py
```