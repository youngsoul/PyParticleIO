
// This #include statement was automatically added by the Particle IDE.
#include <InternetButton.h>

// Declare Variables
// Variable data types:  int, double, String (622 maximum characters)
int int_variable = 0;
double double_variable = 0.0;
String string_variable = "";

bool button2Pressed = false;
bool button3Pressed = false;

// Declare instance of internet button
InternetButton b = InternetButton();

// Define cloud function
int showRainbowFunction(String commmand) {
    // command parameter is not used but it must be part
    // of signature
    b.rainbow(10);
    b.allLedsOff();
    int_variable = 0;
}

void setup() {
    // start the internet button
    b.begin();

    // initialize variables
    int_variable = 0;
    double_variable = 0.0;
    string_variable = "";

    // Define variables to Particle cloud
    Particle.variable("variable1", int_variable);
    Particle.variable("variable2", double_variable);
    Particle.variable("variable3", string_variable);

    //Define function to Particle cloud
    Particle.function("showRainbow", showRainbowFunction);

    // Show rainbow at startup
    b.rainbow(10);
    b.allLedsOff();
}

void loop() {

    if(b.buttonOn(2) && button2Pressed == false) {
        button2Pressed = true;
        int_variable = int_variable + 1;
        double_variable = int_variable * 3.14;
        string_variable = String(int_variable);
        b.ledOn(2,0,0,128);
        delay(1000);
        b.ledOff(2);
    }

    if(int_variable > 3) {
        b.ledOn(6, 64,0,0);
    }

    if(b.buttonOn(3) && button3Pressed == false) {
        button3Pressed = true;
        Particle.publish("IB1_BUTTON3", "", 60, PRIVATE);
        b.ledOn(7,0,64,0);
    }

    if( !b.buttonOn(2) ) {
        button2Pressed = false;
    }
    if( !b.buttonOn(3) ) {
        button3Pressed = false;
    }

}
