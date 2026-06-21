// MQTT Configuration
const MQTT_CONFIG = {
    broker: '103.151.63.82',
    port: 8084, // WebSocket port (standard is 8084 for WS, 8883 for WSS)
    topic: 'proyek/mandiri',
    clientId: `ammonia-dashboard-${Math.random().toString(16).substr(2, 9)}`
};

// Global MQTT Client
let mqttClient = null;

// Initialize MQTT Connection
function initMQTT() {
    console.log('Initializing MQTT connection...');
    console.log(`Connecting to: ${MQTT_CONFIG.broker}:${MQTT_CONFIG.port}`);
    console.log(`Topic: ${MQTT_CONFIG.topic}`);
    
    try {
        if (!window.Paho || !window.Paho.MQTT) {
            console.error('Paho MQTT library not loaded!');
            updateMQTTStatus('error', 'Library Error');
            return;
        }
        
        mqttClient = new Paho.MQTT.Client(
            MQTT_CONFIG.broker,
            parseInt(MQTT_CONFIG.port),
            MQTT_CONFIG.clientId
        );

        console.log('MQTT Client created:', mqttClient);
        
        // Set event callbacks
        mqttClient.onConnectionLost = onConnectionLost;
        mqttClient.onMessageArrived = onMessageArrived;

        // Connect with options
        const connectOptions = {
            onSuccess: onMQTTConnect,
            onFailure: onMQTTFailure,
            useSSL: false,
            reconnect: true,
            cleanSession: false,
            timeout: 30
        };

        console.log('Connecting with options:', connectOptions);
        mqttClient.connect(connectOptions);
    } catch (error) {
        console.error('MQTT Connection Error:', error);
        console.error('Error details:', error.message);
        updateMQTTStatus('error', 'Connection Error: ' + error.message);
    }
}

// On MQTT Connect Success
function onMQTTConnect() {
    console.log('MQTT Connected Successfully');
    updateMQTTStatus('connected', 'MQTT Connected');
    
    // Subscribe to topic
    mqttClient.subscribe(MQTT_CONFIG.topic, {
        onSuccess: function() {
            console.log(`Successfully subscribed to: ${MQTT_CONFIG.topic}`);
        },
        onFailure: function(error) {
            console.error('Subscribe failed:', error);
        }
    });
}

// On MQTT Connect Failure
function onMQTTFailure(error) {
    console.error('MQTT Connection Failed:', error);
    updateMQTTStatus('error', 'Connection Failed');
    
    // Retry connection after 5 seconds
    setTimeout(() => {
        console.log('Retrying MQTT connection...');
        initMQTT();
    }, 5000);
}

// On Connection Lost
function onConnectionLost(responseObject) {
    console.warn('MQTT Connection Lost:', responseObject.errorMessage);
    updateMQTTStatus('disconnected', 'Disconnected');
    
    // Try to reconnect
    if (!responseObject.errorCode === 0) {
        console.log('Attempting to reconnect...');
        setTimeout(() => initMQTT(), 3000);
    }
}

// On Message Arrived
function onMessageArrived(message) {
    console.log('Message received:', message.payloadString);
    
    try {
        const data = JSON.parse(message.payloadString);
        // Handle sensor format: {"mq135":220.00,"temp":28.60,"hum":79.20}
        let sensorData = data;
        if (data.mq135 !== undefined) {
            sensorData = { 
                value: data.mq135,
                ammonia: data.mq135,
                mq135: data.mq135,
                temp: data.temp,
                humidity: data.hum,
                timestamp: Date.now()
            };
        }
        handleSensorData(sensorData);
    } catch (error) {
        console.error('Error parsing MQTT message:', error);
        // Try to handle as plain number
        const value = parseFloat(message.payloadString);
        if (!isNaN(value)) {
            handleSensorData({ value: value, timestamp: Date.now() });
        }
    }
}

// Update MQTT Status Indicator
function updateMQTTStatus(status, text) {
    const statusElement = document.getElementById('apiStatus');
    const statusIndicator = document.getElementById('statusIndicator');
    
    if (statusElement && statusIndicator) {
        statusIndicator.textContent = text;
        
        // Update color based on status
        const statusDot = statusElement.querySelector('i');
        if (statusDot) {
            statusDot.style.color = status === 'connected' ? '#10b981' : 
                                    status === 'disconnected' ? '#ef4444' : '#f59e0b';
        }
    }
}

// Initialize MQTT when document is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard loaded, initializing MQTT...');
    initMQTT();
});
