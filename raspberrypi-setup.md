
# 🧭 Raspberry Pi - Anleitung: Web-App Deployment via Docker

Diese Schritt-für-Schritt-Anleitung beschreibt, wie man eine in **Python** geschriebene **Web-API** (z.B. mit Flask) auf einem **Raspberry Pi** mit Hilfe von **Docker** deployen kannst.

> **Hinweis:** Platzhalter wie `<...>` müssen durch deine individuellen Werte ersetzt werden (z.B. `<connection profile>` -> `Wired connection 1`).


## 🗂️ Übersicht: Schritte im Deployment-Prozess

### In dieser Anleitung werden folgende Schritte durchlaufen:

1. **Netzwerkkonfiguration**  
   Vergabe einer statischen IP-Adresse für den Raspberry Pi per nmcli, um ihn dauerhaft im Netzwerk erreichbar zu machen.

2. **Docker installieren und vorbereiten**  
   Einrichtung der Container-Laufzeitumgebung auf dem Raspberry Pi.

3. **Anwendung vorbereiten**  
   Übertragung der Python-Datei auf den Pi und Vorbereitung des App-Verzeichnisses.

4. **Dockerfile erstellen**  
   Definition des Container-Images, das die Python-Anwendung ausführt.

5. **Image bauen und starten**  
   Erstellen und Ausführen des Docker-Containers, der die Web-API hostet.

6. **Test und Zugriff**  
   Aufrufen der API über den Browser und Überprüfung der Funktion.


## 🔌 1. Netzwerkkonfiguration via `NetworkManager`

Da der Raspberry Pi als Server eingesetzt wird, muss ihm eine **statische IP-Adresse** zugewiesen werden, um ihn im Netzwerk eindeutig und dauerhaft erreichen zu können.


### 🔍 Erklärung: `nmcli`
`nmcli` ist ein Kommandozeilenwerkzeug zur Verwaltung von Netzwerkverbindungen unter Linux - insbesondere mit dem NetworkManager. Damit lassen sich Netzwerkprofile konfigurieren, aktivieren, deaktivieren usw.

### 1.1 Verfügbare Verbindungen anzeigen

```bash
sudo nmcli -p connection show
```

Dieser Befehl zeigt alle eingerichteten Verbindungen an. Entscheide anhand des Anschlusses, ob WLAN (z.B. `wlan0`) LAN (`eth0`) verwendet wird. Meistens wird LAN empfohlen (stabiler, schneller).

### 1.2 Statische IP-Adresse setzen

```bash
sudo nmcli c mod "<connection profile>" ipv4.addresses <IP>/<Subnetzmaske> ipv4.method manual
```

**Beispiel:** `192.168.1.100/24` bedeutet eine IP im Netz `192.168.1.x` mit Subnetzmaske `255.255.255.0`.

### 1.3 IP-Adresse überprüfen

```bash
ifconfig
```

Hier sollte unter dem entsprechenden Interface (`eth0` oder `wlan0`) die soeben konfigurierte IP-Adresse erscheinen.

### 1.4 Gateway definieren

```bash
sudo nmcli con mod "<connection profile>" ipv4.gateway <Gateway-IP>
```

Das Gateway ist in der Regel der Router - z.B. `192.168.1.1`.

### 1.5 Gateway überprüfen

```bash
ip route
```

In der ersten Zeile sollte nun das Gateway aufgeführt sein.

### 1.6 DNS-Server einrichten

```bash
sudo nmcli con mod "<connection profile>" ipv4.dns <DNS-IP>
```

Gültige Beispiele: `8.8.8.8` (Google), `192.168.1.1` (lokaler Router), `1.1.1.1` (Cloudflare).

### 1.7 DNS-Konfiguration prüfen

```bash
nmcli device show | grep IP4.DNS
```

Hier wird die aktuell verwendete DNS-Adresse(n) angezeigt.

### 1.8 Netzwerkverbindung neu starten

```bash
sudo nmcli c down "<connection profile>" && sudo nmcli c up "<connection profile>"
```

Dieser Schritt ist notwendig, damit alle Änderungen aktiv werden.



## 🐳 2. Docker installieren und konfigurieren

### 🔍 Was ist Docker?

**Docker** ist eine Plattform zur Erstellung, Auslieferung und Ausführung sogenannter **Container**. Ein Container ist eine abgeschottete Umgebung, die alle Abhängigkeiten, Konfigurationen und den Code einer Anwendung enthält. Dadurch lässt sich die App überall gleich ausführen - unabhängig von Systembibliotheken oder installierter Software.

Einfach gesagt: **"Docker verpackt die Anwendung in ein leichtgewichtiges Paket, das überall läuft."**

### 🔍 Erklärung: `docker.io` vs. `docker`

Man installiert mit `apt install docker.io` die in den Debian-/Ubuntu-Repositories enthaltene Version von Docker. Sie ist meistens nicht die allerneueste, aber stabil und für den Raspberry Pi gut geeignet.

### 2.1 Docker installieren

```bash
sudo apt update
sudo apt install docker.io
```

### 2.2 Docker testen

```bash
sudo docker run hello-world
```

Erfolgreiche Installation wird durch die Meldung `Hello from Docker!` bestätigt.


## 📁 2.3 Vorbereitung: Python-Datei auf den Raspberry Pi bringen

### 🔍 Erklärung: `scp`

`scp` steht für "secure copy". Es kopiert Dateien über SSH von dem lokalen Rechner auf ein anderes System (z.B. dem Raspberry Pi).

### 🔍 Erklärung: `mkdir`

Der Befehl `mkdir` erstellt ein neues Verzeichnis (Ordner). Man brauchst dieses Verzeichnis, um dort die App und das Dockerfile abzulegen.

### 2.3.1 Verzeichnis für App erstellen

```bash
sudo mkdir /app
```

### 2.3.2 Python-Datei kopieren

Auf dem lokalen Rechner im Terminal (im Verzeichnis der Datei):

```bash
scp <lokale_datei.py> pi@<raspberry_ip>:/app
```

Es wird nach dem Passwort des Benutzers `pi` gefragt, sofern SSH-Zugriff aktiv ist.

### 2.4 Docker-Dienst starten (falls nicht automatisch)

```bash
sudo systemctl start docker.service
```

Optional: Automatischer Start beim Boot:

```bash
sudo systemctl enable docker
```

---

## 🏗️ 3. Docker-Image erstellen und App deployen

### 🔍 Erklärung: Dockerfile

Ein `Dockerfile` ist eine Textdatei, die Docker-Anweisungen enthält, um ein **Image** zu erstellen - also ein Bauplan für den Container.

Darin steht z.B.:

- Welche Programmiersprache (z.B. Python)
- Welche Bibliotheken (z.B. Flask)
- Welche Dateien sollen hineinkopiert werden?
- Was soll beim Start ausgeführt werden?

### 🔍 Erklärung: `touch`

Der Befehl `touch` erstellt eine neue, leere Datei.

### 3.1 Dockerfile erstellen

```bash
cd /app
touch Dockerfile
```

Achte auf die **korrekte Groß-/Kleinschreibung**: `Dockerfile` (nicht `DockerFile.txt`).

### 3.2 Inhalt des Dockerfiles

```dockerfile
# Dockerfile

FROM python:3.12-alpine

# Flask installieren
RUN pip install flask

# Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere Datei in Container
COPY <python_file>.py /app

# Start der Anwendung
ENTRYPOINT ["python"]
CMD ["<python_file>.py"]
```

Ersetze `<python_file>` durch den Dateinamen der App, z.B. `main.py`.

### 🔍 Erklärung: `docker build`

```bash
docker image build -t webapp .
```

Dieser Befehl:

- baut ein Docker-Image anhand des `Dockerfile` im aktuellen Verzeichnis (`.`)
- vergibt dem Image das Label (`Tag`) `webapp`

### 3.3 Docker-Image bauen

```bash
sudo docker image build -t webapp .
```

### 🔍 Erklärung: `docker run` mit Parametern

```bash
sudo docker run -p 5000:5000 -d webapp
```

- `-p 5000:5000`: Portweiterleitung von Host zu Container
- `-d`: Detached Mode (läuft im Hintergrund)
- `webapp`: Name des Docker-Images

### 3.4 Container ausführen

```bash
sudo docker run -p 5000:5000 -d webapp
```

### 🔍 Erklärung: `docker ps`

```bash
docker ps
```

-> Zeigt alle **laufenden** Container an, inklusive ID, Image, Namen und Ports.

---

## 🧪 4. Test und Zugriff

- Rufe im Browser auf: `http://<raspberry_ip>:5000`
- Wenn alles korrekt ist, sollte die API erreicht werden können.
