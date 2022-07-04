# TensorFlow Lite for Commodore 64s

Run inferences using TensorFlow Lite for Microcontrollers on a Commodore 64.

![](https://raw.githubusercontent.com/nickbild/tflite_c64/main/media/screen1_lg.jpg)

This project is in no way associated with, or endorsed by, Google Inc.  TensorFlow, the TensorFlow logo and any related marks are trademarks of Google Inc.

## How It Works

![](https://raw.githubusercontent.com/nickbild/tflite_c64/main/media/tflite-c64-overview.jpg)

TensorFlow Lite for Microcontrollers is an open-source machine learning framework in which a TensorFlow model is built and trained on a host computer.  That model is then reduced in size and computational complexity by an exporter that converts it to the TensorFlow Lite format.  For the tiniest of compute platforms — microcontrollers — that model is then converted to a C array containing the model structure and any trained parameters, like weights and biases.  On the microcontroller, an interpreter parses the C array to extract operations and data to run inferences against new input data.

Given that TF Lite for Microcontrollers runs on some heavily resource-constrained devices, I got to wondering whether or not I could run inferences against these models on a Commodore 64.

To do this, I chose not to use an interpreter.  The TF Lite Micro team explains why they did in [their paper](https://arxiv.org/pdf/2010.08678.pdf) (i.e. portability, maintainability).  And that was a good choice for the project to be sure, but I'm dealing with nearly 40 year old hardware, so I cannot afford the overhead of an interpreter.  Instead, I [modified the TF Lite Micro source code](https://github.com/nickbild/tflite_c64/tree/main/tflite-micro) so that when running an interpreter on the host computer, it will emit all of the important details about the model, e.g.: operations to perform, filter values, biases, etc.  Additionally, I analyzed the source code for all operations involved with running the model so that I could reproduce the functionality.

I then parsed that output with a [Python script](https://github.com/nickbild/tflite_c64/blob/main/parse_output_c64.py) to turn it into C64-compatible BASIC (this could be updated to produce 6502 assembly code, but for this proof of concept, BASIC was actually fast enough).

To test things out, I built TensorFlow's [Hello World](https://github.com/tensorflow/tflite-micro/tree/main/tensorflow/lite/micro/examples/hello_world) example that builds and trains a small, 3 layer neural network that learns to approximate the sine function.  After running it on the host computer and emitting the model info, I used my parser to create [this BASIC code](https://github.com/nickbild/tflite_c64/blob/main/neural_net.bas) that can be used to run arbitrary inferences against the neural network on a Commodore 64.  Each inference takes a few seconds to run on a physical C64 computer.

Since the code running on the C64 is the same thing logically as what runs on the host computer (or microcontroller), it performs equally well in all environments.  There is no accuracy reduction from running on the C64.

## Media

 [YouTube Demonstration](https://www.youtube.com/watch?v=D3Ii4mchgnA)

Running a neural network trained to approximate the sine function on a Commodore 64:

![](https://raw.githubusercontent.com/nickbild/tflite_c64/main/media/screen2_lg.jpg)


A short sample of the generated C64 BASIC code ([full listing here](https://github.com/nickbild/tflite_c64/blob/main/neural_net.bas)):

```
10 dim l1(16)
20 dim l2(16)
30 input "enter a number:"; a%
40 a% = int((a% / 0.024574 - 128)+0.5)
50 acc = ((117 + 0) * (a% + 128)) + 6
60 if acc>0 then acc=(acc*1169513172 + 2^30) / 2^31
70 if acc<=0 then acc=(acc*1169513172 + (1-2^30)) / 2^31
80 acc = (int((acc)+0.5) / 2^6) + -128
90 acc = int((acc)+0.5)
100 if acc < -128 then acc = -128
110 if acc > 127 then acc = 127
120 l1(1) = acc
130 acc = ((28 + 0) * (a% + 128)) + 2935
140 if acc>0 then acc=(acc*1169513172 + 2^30) / 2^31
150 if acc<=0 then acc=(acc*1169513172 + (1-2^30)) / 2^31
160 acc = (int((acc)+0.5) / 2^6) + -128
170 acc = int((acc)+0.5)
180 if acc < -128 then acc = -128
190 if acc > 127 then acc = 127
```

## Bill of Materials

- 1 x Commodore 64 computer (or emulator)

## About the Author

[Nick A. Bild, MS](https://nickbild79.firebaseapp.com/#!/)
