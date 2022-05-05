#include "InternetButton.h"

bool button2Pressed = false;

// Declare instance of internet button
InternetButton b = InternetButton();

void myHandler(const char *event, const char *data)
{
    b.ledOn(6, 0,128,0);
    delay(750);
    b.ledOff(6);
}

void setup() {
    // start the internet button
    b.begin();
    b.allLedsOff();

    // only events from my devices
    Particle.subscribe("test_event", myHandler, MY_DEVICES);
}

void loop() {

    if(b.buttonOn(2) && button2Pressed == false) {
        button2Pressed = true;
        b.ledOn(2,0,0,128);
        delay(1000);
        Particle.publish("test_event", "", 60, PRIVATE);
        b.ledOff(2);
    }

    if( !b.buttonOn(2) ) {
        button2Pressed = false;
    }

}
