#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <dht.h>

// Update these with values suitable for your network.
byte mac[] = { 0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED };
IPAddress server(10, 7, 49, 163);

/**
//Uncomment if you want to set a manual IP
IPAddress ip(10, 10, 1, 2);
IPAddress localDns(10, 10, 1, 1);
IPAddress gateway(10, 10, 1, 1);
IPAddress subnet(255, 255, 255, 0);
**/

EthernetClient ethClient;
PubSubClient client(ethClient);

dht DHT;

#define DHT21_PIN 2
#define LED_PIN   3

char* cmdAnswerTopic = "/4jggokgpepnvsb2uv4s40d59ov1/STELA_LED/cmdexe"; // /API_KEY/DEVICE_ID/cmdexe + 5

void setup() {
  Serial.begin(115200);
  delay(2000);

  pinMode(LED_PIN, OUTPUT);

  client.setServer(server, 1883);
  
  Ethernet.begin(mac); //DHCP (auto IP)
  //Ethernet.begin(mac, ip, localDns, gateway, subnet); //Manual IP
  
  delay(1500);  //Allow the hardware to sort itself out
}

void publishMeasurements() {
  char strHumidity[6];
  char strTemperature[6];

  char measurementPayloadBuf[40];
  char measurementPayloadBuf[40];

  int chk = DHT.read21(DHT21_PIN);
  switch (chk){
    case DHTLIB_OK:
      dtostrf(DHT.humidity, 4, 2, strHumidity);
      dtostrf(DHT.temperature, 4, 2, strTemperature);

      sprintf(measurementPayloadBuf, "h|%s|t|%s", strHumidity, strTemperature);
      Serial.println(measurementPayloadBuf);

      client.publish("/4jggokgpepnvsb2uv4s40d59ov1/STELA_DHT/attrs", measurementPayloadBuf);

      delay(60000);
      break;
    default:
      Serial.println("Failed to read sensor. Trying again in 2 seconds.");
      delay(2000);
      break;
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
	Serial.print("Message arrived [");
	Serial.print(topic);
	Serial.println("] ");

	//for (int i=0; i < length; i++) {
	//	Serial.print((char)payload[i]);
	//}

	if (cmd.strcmp((char *) payload, "ON")) {
		digitalWrite(LED_PIN, HIGH);
		client.publish(cmdAnswerTopic, "change_state|Done");
	} else if (cmd.strcmp((char *) payload, "OFF")) {
		digitalWrite(LED_PIN, LOW);
		client.publish(cmdAnswerTopic, "change_state|Done");
	} else {
		client.publish(cmdAnswerTopic, "change_state|Error");
	}

	Serial.println("Answer sent");
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to server...");
    if (!client.connect("arduinoClient")) {
      Serial.println("Connection failed. Trying again in 2 seconds.");
      delay(2000); // Wait until try again
    }
  }
}

void loop() {
  if (client.connected()){
    publishMeasurements();
  } else {
    reconnect();
  }
  client.loop();
}
