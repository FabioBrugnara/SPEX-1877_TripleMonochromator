#include <Arduino.h>

// DEFINITION OF PROGRAM CONSTANTS

const byte numChars = 40;       // lenght of the recived command (in chars)
char Command[numChars];   // an array to store the received command
char splitCom[4][numChars]; // an array to split the command
char StopCommand[numChars];   // an array to store the received command

boolean newCommand = false;
boolean newStopCommand = false;


// PINSS


int specDirPin = 2;
int specClockPin = 3;
int specStopcw = 4;
int specStopccw = 5;

int filterDirPin = 6;
int filterClockPin = 7;
int filterStopcw = 8;
int filterStopccw = 9;


// MOTORS parameter

int specMotorMaxSpeed = 200; // steps per second
int specMotorSpeed = specMotorMaxSpeed; // steps per second
int filterMotorMaxSpeed = 200; // steps per second
int filterMotorSpeed = filterMotorMaxSpeed; // steps per second

int specPos;
int filterPos;
 
// SETUP

void setup() {
  Serial.begin(115200);

  specPos = 0; // initial position of the spectrometer
  filterPos = 0; // initial position of the filter

  // Initialize pins

  // built-in LED
  pinMode(LED_BUILTIN, OUTPUT);

  // spectrometer
  pinMode(specDirPin, OUTPUT);
  pinMode(specClockPin, OUTPUT);
  pinMode(specStopcw, INPUT);
  pinMode(specStopccw, INPUT);

  // filter
  pinMode(filterDirPin, OUTPUT);
  pinMode(filterClockPin, OUTPUT);
  pinMode(filterStopcw, INPUT);
  pinMode(filterStopccw, INPUT);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////
// FUNCTIONS//
//////////////

void readCommand() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;

    while (Serial.available() > 0 && newCommand == false) {
        rc = Serial.read();
        if (rc != endMarker) {
            Command[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            Command[ndx] = '\0'; // terminate the string
            ndx = 0;
            newCommand = true;
        }
    }
}


void splitCommand(char str1[]) {
// local variables declaration
  unsigned int i,j=0,ctr=0;

  for(i=0;i<=(strlen(str1));i++) {
      // if space or NULL found, assign NULL into newString[ctr]
      if(str1[i]==' '||str1[i]=='\0')
      {
          splitCom[ctr][j]='\0';
          ctr++;  //for next word
          j=0;    //for next word, init index to 0
      }
      else
      {
          splitCom[ctr][j]=str1[i];
          j++;
      }
    }
}

////////////////////////////////
// control spec stepper motor //
////////////////////////////////

void specJump(int steps) {

  int error = 0;


  // set direction
  int dir = steps/abs(steps);
  if (dir == 1)
    digitalWrite(specDirPin, HIGH);
  else 
    digitalWrite(specDirPin, LOW);

  // set speed
  int stepDelay = 1000/specMotorSpeed/2; // in ms

  // do steps
  for (int i = 0; i < abs(steps); i++) {

    // check if stop command is received, if any other command is received, ignore it
    if (Serial.available()>0){
      static byte ndx = 0;
      char endMarker = '\n';
      char rc;
        newStopCommand = false;
      while (Serial.available() > 0 && newStopCommand == false) {
          rc = Serial.read();
          if (rc != endMarker) {
              StopCommand[ndx] = rc;
              ndx++;
              if (ndx >= numChars) {
                  ndx = numChars - 1;
              }
          }
          else {
              StopCommand[ndx] = '\0'; // terminate the string
              ndx = 0;
              newStopCommand = true;
          }
        if (strcmp(StopCommand, "stop") == 0){
          break;
        }
      }
    }    

    // check if limit switch is reached
    if (digitalRead(specStopcw) == HIGH && dir == 1){
      error = 1;
      break; }
    else if (digitalRead(specStopccw) == HIGH && dir == -1){
      error = -1;
      break; }
    else {
      digitalWrite(specClockPin, HIGH);
      delay(stepDelay);
      digitalWrite(specClockPin, LOW);
      delay(stepDelay);

      specPos = specPos + dir;}
  }


  // print position
  Serial.print(specPos);
  Serial.print("\n");

  if (error == 1)
    Serial.print("error: clockwise limit reached\n");
  else if (error == -1)
    Serial.print("error: counter-clockwise limit reached\n");
  else
    Serial.print("ok\n");
}


void specGoto(int pos) {

  int dir;
  int error = 0;


  // set direction
  if (pos > specPos) {
    dir = 1;
    digitalWrite(specDirPin, HIGH);
  }
  else {
    dir = -1;
    digitalWrite(specDirPin, LOW);
  }

  // set speed
  int stepDelay = 1000/specMotorSpeed/2; // in ms

  // do steps
  while (specPos != pos) {

    // check if stop command is received, if any other command is received, ignore it
    if (Serial.available()>0){
      static byte ndx = 0;
      char endMarker = '\n';
      char rc;
        newStopCommand = false;
      while (Serial.available() > 0 && newStopCommand == false) {
          rc = Serial.read();
          if (rc != endMarker) {
              StopCommand[ndx] = rc;
              ndx++;
              if (ndx >= numChars) {
                  ndx = numChars - 1;
              }
          }
          else {
              StopCommand[ndx] = '\0'; // terminate the string
              ndx = 0;
              newStopCommand = true;
          }
        if (strcmp(StopCommand, "stop") == 0){
          break;
        }
      }
    }    

    if (digitalRead(specStopcw) == HIGH && dir == 1){
      error = 1;
      break; }
    else if (digitalRead(specStopccw) == HIGH && dir == -1){
      error = -1;
      break; }
    else {
      digitalWrite(specClockPin, HIGH);
      delay(stepDelay);
      digitalWrite(specClockPin, LOW);
      delay(stepDelay);

      specPos = specPos + dir; }
  }


  // print position
  Serial.print(specPos);
  Serial.print("\n");

  if (error == 1)
    Serial.print("error: clockwise limit reached\n");
  else if (error == -1)
    Serial.print("error: counter-clockwise limit reached\n");
  else
    Serial.print("ok\n");
}


//////////////////////////////////
// control filter stepper motor //
//////////////////////////////////

void filterJump(int steps) {

  int error = 0;


  // set direction
  int dir = steps/abs(steps);
  if (dir == 1)
    digitalWrite(filterDirPin, HIGH);
  else 
    digitalWrite(filterDirPin, LOW);

  // set speed
  int stepDelay = 1000/filterMotorSpeed/2; // in ms

  // do steps
  for (int i = 0; i < abs(steps); i++) {

    // check if stop command is received, if any other command is received, ignore it
    if (Serial.available()>0){
      static byte ndx = 0;
      char endMarker = '\n';
      char rc;
        newStopCommand = false;
      while (Serial.available() > 0 && newStopCommand == false) {
          rc = Serial.read();
          if (rc != endMarker) {
              StopCommand[ndx] = rc;
              ndx++;
              if (ndx >= numChars) {
                  ndx = numChars - 1;
              }
          }
          else {
              StopCommand[ndx] = '\0'; // terminate the string
              ndx = 0;
              newStopCommand = true;
          }
        if (strcmp(StopCommand, "stop") == 0){
          break;
        }
      }
    }
    
    // check if limit switch is reached
    if (digitalRead(filterStopcw) == HIGH && dir == 1){
      error = 1;
      break; }
    else if (digitalRead(filterStopccw) == HIGH && dir == -1){
      error = -1;
      break; }
    else {
      digitalWrite(filterClockPin, HIGH);
      delay(stepDelay);
      digitalWrite(filterClockPin, LOW);
      delay(stepDelay);

      filterPos = filterPos + dir;}
  }


  // print position
  Serial.print(filterPos);
  Serial.print("\n");

  if (error == 1)
    Serial.print("error: clockwise limit reached\n");
  else if (error == -1)
    Serial.print("error: counter-clockwise limit reached\n");
  else
    Serial.print("ok\n");
}


void filterGoto(int pos) {

  int dir;
  int error = 0;


  // set direction
  if (pos > filterPos) {
    dir = 1;
    digitalWrite(filterDirPin, HIGH);
  }
  else {
    dir = -1;
    digitalWrite(filterDirPin, LOW);
  }

  // set speed
  int stepDelay = 1000/filterMotorSpeed/2; // in ms

  // do steps
  while (filterPos != pos) {

    // check if stop command is received, if any other command is received, ignore it
    if (Serial.available()>0){
      static byte ndx = 0;
      char endMarker = '\n';
      char rc;
        newStopCommand = false;
      while (Serial.available() > 0 && newStopCommand == false) {
          rc = Serial.read();
          if (rc != endMarker) {
              StopCommand[ndx] = rc;
              ndx++;
              if (ndx >= numChars) {
                  ndx = numChars - 1;
              }
          }
          else {
              StopCommand[ndx] = '\0'; // terminate the string
              ndx = 0;
              newStopCommand = true;
          }
        if (strcmp(StopCommand, "stop") == 0){
          break;
        }
      }
    }    

    if (digitalRead(filterStopcw) == HIGH && dir == 1){
      error = 1;
      break; }
    else if (digitalRead(filterStopccw) == HIGH && dir == -1){
      error = -1;
      break; }
    else {
      digitalWrite(filterClockPin, HIGH);
      delay(stepDelay);
      digitalWrite(filterClockPin, LOW);
      delay(stepDelay);

      filterPos = filterPos + dir; }
  }


  // print position
  Serial.print(filterPos);
  Serial.print("\n");

  if (error == 1)
    Serial.print("error: clockwise limit reached\n");
  else if (error == -1)
    Serial.print("error: counter-clockwise limit reached\n");
  else
    Serial.print("ok\n");
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////
// MAIN LOOP//
//////////////

void loop() {

  // set pins to low
  digitalWrite(specClockPin, LOW);
  digitalWrite(filterClockPin, LOW);

  readCommand();
  
  if (newCommand == true) {

    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print(Command);    // echo the command
    Serial.print("\n");

    splitCommand(Command);   // split the command

    // GLOBAL COMMANDS
    if (strcmp(Command, "status") == 0)
        Serial.print("ok\n");

    else if (strcmp(Command, "whoareyou") == 0){
      Serial.print("Spex motors micro-controller\n");
      Serial.print("ok\n"); }

    else if (strcmp(Command, "stop") == 0){ }

    else if (strcmp(Command, "help") == 0){
      Serial.print("status\n");
      Serial.print("whoareyou\n");
      Serial.print("stop\n");
      Serial.print("help\n");
      Serial.print("spec set_speed <speed>\n");
      Serial.print("spec read_speed\n");
      Serial.print("spec read_pos\n");
      Serial.print("spec goto <pos>\n");
      Serial.print("spec jump <steps>\n");
      Serial.print("filter set_speed <speed>\n");
      Serial.print("filter read_speed\n");
      Serial.print("filter read_pos\n");
      Serial.print("filter goto <pos>\n");
      Serial.print("filter jump <steps>\n");
      Serial.print("ok\n"); }

    // SPECTROMETER COMMANDS
    else if (strcmp(splitCom[0], "spec") == 0) {

      if (strcmp(splitCom[1], "set_speed") == 0){
        if (atoi(splitCom[2]) > 0 && atoi(splitCom[2]) <= specMotorMaxSpeed){
          specMotorSpeed = atoi(splitCom[2]);
          Serial.print("ok\n"); }
        else
          Serial.print("error: speed out of range\n");
      }
      else if (strcmp(splitCom[1], "read_speed") == 0){
        Serial.print(specMotorSpeed);
        Serial.print("\n");
        Serial.print("ok\n"); }

      else if (strcmp(splitCom[1], "read_pos") == 0){
        Serial.print(specPos);
        Serial.print("\n");

        if (digitalRead(specStopcw) == HIGH)
          Serial.print("error: clockwise limit reached\n");
        else if (digitalRead(specStopccw) == HIGH)
          Serial.print("error: counter-clockwise limit reached\n");
        else
          Serial.print("ok\n"); }


      else if (strcmp(splitCom[1], "init_pos") == 0){
        specPos = 0;
        Serial.print("ok\n"); }

      else if (strcmp(splitCom[1], "goto") == 0)
        specGoto(atoi(splitCom[2]));
      
      else if (strcmp(splitCom[1], "jump") == 0)
        specJump(atoi(splitCom[2]));
      else
        Serial.print("error: unknown command\n");
    }

    // FILTER
    else if (strcmp(splitCom[0], "filter") == 0) {
        
        if (strcmp(splitCom[1], "set_speed") == 0){
          if (atoi(splitCom[2]) > 0 && atoi(splitCom[2]) <= filterMotorMaxSpeed){
            filterMotorSpeed = atoi(splitCom[2]);
            Serial.print("ok\n"); }
          else
            Serial.print("error: speed out of range\n");
        }
        else if (strcmp(splitCom[1], "read_speed") == 0){
          Serial.print(filterMotorSpeed);
          Serial.print("\n");
          Serial.print("ok\n"); }
  
        else if (strcmp(splitCom[1], "read_pos") == 0){
          Serial.print(filterPos);
          Serial.print("\n");
  
          if (digitalRead(filterStopcw) == HIGH)
            Serial.print("error: clockwise limit reached\n");
          else if (digitalRead(filterStopccw) == HIGH)
            Serial.print("error: counter-clockwise limit reached\n");
          else
            Serial.print("ok\n"); }
  
        else if (strcmp(splitCom[1], "init_pos") == 0){
          filterPos = 0;
          Serial.print("ok\n"); }
  
        else if (strcmp(splitCom[1], "goto") == 0)
          filterGoto(atoi(splitCom[2]));
        
        else if (strcmp(splitCom[1], "jump") == 0)
          filterJump(atoi(splitCom[2]));
        else
          Serial.print("error: unknown command\n");
    }

    // ERROR: NOT A COMMAND
    else
        Serial.print("error: unknown command\n");
    }
    
  digitalWrite(LED_BUILTIN, LOW);
  newCommand = false;
}

