// This #include statement was automatically added by the Particle IDE.
#include <InternetButton.h>

InternetButton b = InternetButton();
bool button1Pressed = false;


void setup() {
    b.begin();
}

void loop() {
    if(b.buttonOn(1) && button1Pressed == false) {
        button1Pressed = true;
        Particle.publish("button1","", 60, PRIVATE);
    }

    if(b.allButtonsOff()) {
        button1Pressed = false;
    }
}
