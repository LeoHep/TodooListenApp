# Raspberry Pi - Anleitung Web App Deployement via Raspberry Pi

Dies ist eine Schritt-für-Schritt-Anleitung zum Deployment einer in Python geschriebenen API auf einem Raspberry Pi mittels Docker.

#### Info: die <> klammern dienen als platzhalter, dort sollten Werte eingefügt werden

## 1. Netzwerkkonfiguration via Networkmanager 

Da der Raspberry PI als Server genutzt wird muss eine statische IP Adresse vergeben werden. Die Netwerkkonfiguration läuft wie folgt ab:

### 1.1 Korrektes connection profile raussuchen

Mit dem Befehl:

```bash
sudo nmcli -p connection show
```

lassen sich alle connection profiles ausgeben. Um mit den weiteren schritten fortfahren zu können muss geklärt werden, ob eine WLAN oder Kabelverbindung besteht. Meistens kann das Ethernet Profil eth0 (Wired connection 1) genutzt werden.

### 1.2 Ip Adresse festlegen

````
$ sudo nmcli c mod "<connection profile>" ipv4.addresses <ip/subnetzmaske> ipv4.method Manual
````

### 1.3 IP Adresse nach korrektheit prüfen

````
$ ifconfig
````

hat man z.B. eth0 konfiguriert sollte hier unter eth0 die IP erscheinen die bei Punkt 1.2 konfiguriert wurde. 

### 1.4 Gateway festlegen 

````
$ sudo nmcli con mod "<connection profile>" ipv4.gateway <ip>
````

### 1.5 Gateway prüfen

````
$ ip route
````

in der ersten Zeile sollte die in Punkt 1.4 hinterlegte IP zufinden sein. 

### 1.6 DNS festlegen

````
$ sudo nmcli con mod "Wired connection 1" ipv4.dns 10.0.0.1 (192.168.24.254 oder 172.28.28)
````

### 1.7 DNS Konfiguration prüfen 

Um die korrektheit der DNS Konfiguration zu prüfen kann folgender Befehl verwendet werden:

````
$ nmcli device show | grep IP4.DNS
````

### 1.8 Netzwerkverbindung neustarten 

Um die Konfigurationen vollständig zu übernehmen, muss folgender Befehl ausgeführt werden: '
'
````
$ sudo nmcli c down "<connection profile>" && sudo nmcli c up "<connection profile>"
````

### 2. Aufsetzen von Docker 

Docker wird verwendet, um die Web-App (in diesem Fall eine Python-Flask-API) in einem isolierten Container auszuführen. Dadurch ist sichergestellt, dass alle notwendigen Abhängigkeiten, Bibliotheken und die Laufzeitumgebung einheitlich und unabhängig vom Raspberry Pi System bereitgestellt werden können.

### 2.1 Docker installieren 

Für die Installation von Docker wird der `apt` packet manager vom Raspberry Pi verwendet.

````
$ sudo apt install docker.io
````

### 2.2 Docker Installation testen 

````
$ sudo docker run hello-world
````

Dieser Befehl sollte in der Konsole ein `Hello from docker` anzeigen.

### 2.3 Python Datei auf den Raspberry Pi kopieren

Um das Docker Image basierend auf der Python API bauen zu können, muss der Python File erst auf den Raspberry Pi kopiert werden. 

### 2.3.1 Verzeichniss für die app erstellen 

Um einen Ordner erstellen zu können in den die wichtigen Files für die app kommen verwendet man den Befehl `mkdir`. Der Ordner wird in diesem Fall auf der obersten Ebene der Ordnerstruktur erstellt: 

````
$ sudo mkdir /app
````

### 2.4 Python File auf Raspberry Pi kopieren

Um den FIle nun auf den Raspberry Pi zu kopieren muss die Konsole (CMD), in dem Pfad wo sich der Python File befindet, auf dem lokalen PC geöffnet werden. Dann kann wie folgt der Python File auf den Raspberry Pi kopiert werden: 

````
scp <lokale_datei> pi@<raspberry_ip>:/ziel/pfad
````
Falls der angegeben User passwortgeschützt ist muss ebenfalls das Passwort angegeben werden. 

### 2.5 Starte des Docker Dienstes 

Nach der Installation ist Docker muss der Docker-Dienst eventuell noch gestartet werden, bevor neue Container
eingerichtet werden können:

````
$ sudo systemctl start docker.service
````

### 2.6 Erstellen eines neuen Docker Images


### 2.6.1 Erstellung des Docker Files

Die Datei muss Dockerfile heißen:

````
$ sudo touch DockerFile.txt
````
### 2.6.2 Die Dockerfile Datei anpassen

Die Datei sollte wie folgt aussehen:

````
# Dockerfile

# Basisimage für Python-Anwendungen herunterladen
FROM python:3.8-alpine

# Notwendige Bibliotheken installieren
RUN pip install flask

# Arbeitsverzeichnis im Container wechseln
WORKDIR /app

# Kopiere lokale Datei in das Container-Image
COPY <Python file> /app

# Konfiguriere den Befehl, der im Container ausgeführt werden soll
# (Anwendung Python + Skriptname als Parameter)
ENTRYPOINT [ "python" ]
CMD ["<Python File>" ]
````

### 2.6.3 Image für den Docker Container bauen 

Anschließend kann das Image für den neuen Container gebaut werden:

````
$ sudo docker image build -t <container name> .
````

### 2.7 Ausführen des Images in dem angelegten Container 

Nach dem erfolgreichen Bauen kann der Container mit diesem Image gestartet werden:

````
$ sudo docker run -p 5000:5000 -d webapp
````

### 2.8 Laufende Docker Container anzeigen 

````
$ sudo docker ps
````


