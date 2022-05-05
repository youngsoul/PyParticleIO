// This #include statement was automatically added by the Particle IDE.
#include "InternetButton/InternetButton.h"

InternetButton b = InternetButton();
void onRainbowHandler(String event, String data)
{
    b.rainbow(10);
    b.allLedsOff();
}

void setup() {
    b.begin();

    onRainbowHandler("","");

    Particle.subscribe("showRainbow", onRainbowHandler, MY_DEVICES);

}

void loop() {

    // Wait a bit
    delay(100);
}
