// This #include statement was automatically added by the Particle IDE.
#include <InternetButton.h>

InternetButton b = InternetButton();

int turnOnLed(String cmd) {
    if(cmd == "led1") {
        b.ledOn(1,0,0,64);
    } else if( cmd == "led2") {
        b.ledOn(2, 0,0,64);
    }

    return 1;
}

int turnOffLed(String cmd) {
    if(cmd == "led1") {
        b.ledOff(1);
    } else if( cmd == "led2") {
        b.ledOff(2);
    }

    return 1;
}

void setup() {
    b.begin();
    Particle.function("ledOn", turnOnLed);
    Particle.function("ledOff", turnOffLed);
}

void loop() {
// Notice - there is nothing to do in the loop method
// we are waiting for the defined Particle functions
// to be called
}
