input_offsets = []
filter_vals = []
filter_offsets = []
bias_data = []
output_multiplier = []
output_offset = []
right_shift = []
output_scale = []
output_zero_point = []


# Parse relevant values from TF output log.
for line in open("output.txt"):
    line = line.strip()
    
    if line.startswith("NAB FULLY CONNECTED EXEC FILTER VAL "):
        filter_vals.append(line.replace("NAB FULLY CONNECTED EXEC FILTER VAL ", ""))

    elif line.startswith("NAB FULLY CONNECTED EXEC FILTER OFFSET "):
        filter_offsets.append(line.replace("NAB FULLY CONNECTED EXEC FILTER OFFSET ", ""))

    elif line.startswith("NAB FULLY CONNECTED EXEC INPUT OFFSET "):
        input_offsets.append(line.replace("NAB FULLY CONNECTED EXEC INPUT OFFSET ", ""))

    elif line.startswith("NAB FULLY CONNECTED EXEC BIAS DATA "):
        bias_data.append(line.replace("NAB FULLY CONNECTED EXEC BIAS DATA ", ""))

    elif line.startswith("NAB FULLY CONNECTED OUTPUT MULTIPLIER "):
        output_multiplier.append(line.replace("NAB FULLY CONNECTED OUTPUT MULTIPLIER ", ""))

    elif line.startswith("NAB FULLY CONNECTED RIGHT SHIFT "):
        right_shift.append(line.replace("NAB FULLY CONNECTED RIGHT SHIFT ", ""))

    elif line.startswith("NAB FULLY CONNECTED EXEC OUTPUT OFFSET "):
        output_offset.append(line.replace("NAB FULLY CONNECTED EXEC OUTPUT OFFSET ", ""))

    elif line.startswith("NAB OUTPUT SCALE "):
        output_scale.append(line.replace("NAB OUTPUT SCALE ", ""))

    elif line.startswith("NAB OUTPUT ZERO POINT "):
        output_zero_point.append(line.replace("NAB OUTPUT ZERO POINT ", ""))


# Generate code as a series of steps to represent the model.
x = 1
l1_input = int(x / 0.024574 - 128)

line_number = 10

print('{0} dim l1(16)'.format(line_number))
line_number += 10

print('{0} dim l2(16)'.format(line_number))
line_number += 10

print('{0} input "enter a number:"; a%'.format(line_number))
line_number += 10
print('{0} a% = int((a% / 0.024574 - 128)+0.5)'.format(line_number))
line_number += 10

l1_results = []
l2_results = []

# Layer 1

for i in range(16):
    acc = (int(filter_vals[i]) + int(filter_offsets[i])) * (l1_input + int(input_offsets[i]))
    acc += int(bias_data[i])

    print('{0} acc = (({1} + {2}) * (a% + {3})) + {4}'.format(line_number, int(filter_vals[i]), int(filter_offsets[i]), int(input_offsets[i]), int(bias_data[i])))
    line_number += 10
    
    if acc > 0:
        acc = (acc * int(output_multiplier[i]) + 2**30) / 2**31
    else:
        acc = (acc * int(output_multiplier[i]) + (1 - 2**30)) / 2**31

    print('{0} if acc>0 then acc=(acc*{1} + 2^30) / 2^31'.format(line_number, int(output_multiplier[i])))
    line_number += 10
    print('{0} if acc<=0 then acc=(acc*{1} + (1-2^30)) / 2^31'.format(line_number, int(output_multiplier[i])))
    line_number += 10

    acc = int(int(acc) / 2**int(right_shift[i]))
    acc += int(output_offset[i])

    print('{0} acc = (int((acc)+0.5) / 2^{1}) + {2}'.format(line_number, int(right_shift[i]), int(output_offset[i])))
    line_number += 10
    print('{0} acc = int((acc)+0.5)'.format(line_number))
    line_number += 10

    if acc < -128:
        acc = -128
    elif acc > 127:
        acc = 127

    print('{0} if acc < -128 then acc = -128'.format(line_number))
    line_number += 10
    print('{0} if acc > 127 then acc = 127'.format(line_number))
    line_number += 10

    l1_results.append(acc)

    print('{0} l1({1}) = acc'.format(line_number, i+1))
    line_number += 10

# print('{0} for i=1 to 16'.format(line_number))
# line_number += 10
# print('{0} print l1(i)'.format(line_number))
# line_number += 10
# print('{0} next i'.format(line_number))
# line_number += 10

# Layer 2

for node in range(16):
    acc = 0

    print('{0} acc = 0'.format(line_number))
    line_number += 10

    for l1 in range(16):
        offset = 16 + (node*16) + l1
        acc += (int(filter_vals[offset]) + int(filter_offsets[offset])) * (l1_results[l1] + int(input_offsets[offset]))

        print('{0} acc = acc + (({1} + {2}) * (l1({3}) + {4}))'.format(line_number, int(filter_vals[offset]), int(filter_offsets[offset]), l1+1, int(input_offsets[offset]) ))
        line_number += 10
    
    acc += int(bias_data[node+16])

    print('{0} acc = acc + {1}'.format(line_number, int(bias_data[node+16])))
    line_number += 10

    if acc > 0:
        acc = (acc * int(output_multiplier[node+16]) + 2**30) / 2**31
    else:
        acc = (acc * int(output_multiplier[node+16]) + (1 - 2**30)) / 2**31

    print('{0} if acc>0 then acc=(acc*{1} + 2^30) / 2^31'.format(line_number, int(output_multiplier[node+16])))
    line_number += 10
    print('{0} if acc<=0 then acc=(acc*{1} + (1-2^30)) / 2^31'.format(line_number, int(output_multiplier[node+16])))
    line_number += 10


    acc = int(int(acc) / 2**int(right_shift[node+16]))
    acc += int(output_offset[node+16])

    print('{0} acc = (int((acc)+0.5) / 2^{1}) + {2}'.format(line_number, int(right_shift[node+16]), int(output_offset[node+16])))
    line_number += 10
    print('{0} acc = int((acc)+0.5)'.format(line_number))
    line_number += 10

    if acc < -128:
        acc = -128
    elif acc > 127:
        acc = 127

    print('{0} if acc < -128 then acc = -128'.format(line_number))
    line_number += 10
    print('{0} if acc > 127 then acc = 127'.format(line_number))
    line_number += 10

    l2_results.append(acc)

    print('{0} l2({1}) = acc'.format(line_number, node+1))
    line_number += 10

# print('{0} for i=1 to 16'.format(line_number))
# line_number += 10
# print('{0} print l2(i)'.format(line_number))
# line_number += 10
# print('{0} next i'.format(line_number))
# line_number += 10

# Layer 3

acc = 0

print('{0} acc = 0'.format(line_number))
line_number += 10

for l2 in range(16):
    offset = 16 + (16*16) + l2
    acc += (int(filter_vals[offset]) + int(filter_offsets[offset])) * (l2_results[l2] + int(input_offsets[offset]))

    print('{0} acc = acc + (({1} + {2}) * (l2({3}) + {4}))'.format(line_number, int(filter_vals[offset]), int(filter_offsets[offset]), l2+1, int(input_offsets[offset]) ))
    line_number += 10
    

acc += int(bias_data[32])

print('{0} acc = acc + {1}'.format(line_number, int(bias_data[32])))
line_number += 10


if acc > 0:
    acc = (acc * int(output_multiplier[32]) + 2**30) / 2**31
else:
    acc = (acc * int(output_multiplier[32]) + (1 - 2**30)) / 2**31


print('{0} if acc>0 then acc=(acc*{1} + 2^30) / 2^31'.format(line_number, int(output_multiplier[32])))
line_number += 10
print('{0} if acc<=0 then acc=(acc*{1} + (1-2^30)) / 2^31'.format(line_number, int(output_multiplier[32])))
line_number += 10

acc = int(int(acc) / 2**int(right_shift[32]))
acc += int(output_offset[32])


print('{0} acc = (int((acc)+0.5) / 2^{1}) + {2}'.format(line_number, int(right_shift[32]), int(output_offset[32])))
line_number += 10
print('{0} acc = int((acc)+0.5)'.format(line_number))
line_number += 10


if acc < -128:
    acc = -128
elif acc > 127:
    acc = 127

print('{0} if acc < -128 then acc = -128'.format(line_number))
line_number += 10
print('{0} if acc > 127 then acc = 127'.format(line_number))
line_number += 10

print('{0} result = (acc - {1}) * {2}'.format(line_number, int(output_zero_point[0]), float(output_scale[0])))
line_number += 10

print('{0} print result'.format(line_number))
line_number += 10


print(l1_results)
print(l2_results)
print((acc - int(output_zero_point[0])) * float(output_scale[0]))
