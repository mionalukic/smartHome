## **Pokretanje sistema**

**Korak 1 – Pokretanje Docker servisa**

U root folderu projekta (gde se nalazi `docker-compose.yml`) pokrenuti:

docker compose up -d

Ovim se pokreću sledeći servisi:

- **MQTT broker (Mosquitto)** – port `1883`
- **InfluxDB 2.7** – port `8086`
- **Grafana** – port `3000`

Provera da li su servisi aktivni:

docker ps

--------------------------------------------------

**Korak 2 – Pokretanje simulacije senzora**

U folderu gde se nalazi `main.py` pokrenuti:

python main.py --sensors

Ova aplikacija:
- simulira rad senzora (**PIR, ultrasonic, door sensor, light, buzzer**),
- šalje senzorske podatke preko **MQTT** protokola.

U terminalu treba da budu vidljive poruke o radu senzora i MQTT komunikaciji.

--------------------------------------------------

**Korak 3 – Pokretanje MQTT → InfluxDB servisa**

U drugom terminalu, u folderu gde se nalazi `app.py`, pokrenuti:

python app.py

Ovaj servis:
- sluša **MQTT** poruke,
- parsira podatke sa senzora,
- upisuje podatke u **InfluxDB** bazu.

Provera da servis radi:

http://localhost:5000/health

Ako je servis aktivan, vraća se odgovor:

{"status": "ok"}

--------------------------------------------------

**Korak 4 – Grafana (vizualizacija podataka)**

U browseru otvoriti:

http://localhost:3000

Podrazumevani login podaci:
- **username:** admin
- **password:** admin

--------------------------------------------------

**Korak 5 – Import Grafana dashboard-a**

Dashboard je eksportovan kao **JSON** fajl i nalazi se u folderu `grafana/`.

Postupak:
1. U Grafani otvoriti **Dashboards → New → Import**
2. Upload fajl `grafana/dashboard.json`
3. Kao datasource izabrati **InfluxDB**
4. Kliknuti **Import**

Nakon toga, paneli prikazuju senzorske podatke u realnom vremenu.

--------------------------------------------------

**Korak 6 – Provera ispravnosti rada sistema**

Sistem je ispravno pokrenut ako važi:
- MQTT poruke su vidljive u terminalu
- Podaci se pojavljuju u **InfluxDB bucket-u `smarthome`**
- **Grafana** paneli prikazuju vremenske serije senzora
