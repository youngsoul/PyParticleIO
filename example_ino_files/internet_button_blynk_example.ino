// This #include statement was automatically added by the Particle IDE.
#include <blynk.h>

// This #include statement was automatically added by the Particle IDE.
#include <InternetButton.h>

bool button3Pressed = false;

// Declare instance of internet button
InternetButton b = InternetButton();

WidgetLED blynkLed(V0);

BLYNK_WRITE(V1) {
        int value = param.asInt();
        if(value == 1 ) {
            b.allLedsOn(40,0,0);
        } else {
            b.allLedsOn(0,40,40);
        }
}

int gauge_value=0;
BLYNK_READ(V2) {
        gauge_value += 10;
        if(gauge_value > 100) {
            gauge_value = 0;
        }
        Blynk.virtualWrite(V2, gauge_value);
}


void setup() {
    // start the internet button
    b.begin();

    Blynk.begin("blynk app id");

    b.allLedsOff();
}

void loop() {

    Blynk.run();
    if(b.buttonOn(3) && button3Pressed == false) {
        button3Pressed = true;
        blynkLed.on();
        b.ledOn(3,0,64,0);
    }

    if( !b.buttonOn(3) && button3Pressed == true ) {
        button3Pressed = false;
        blynkLed.off();
        b.ledOff(3);
    }

}
