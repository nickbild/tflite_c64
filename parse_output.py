input_offsets = []
filter_vals = []
filter_offsets = []
bias_data = []
output_multiplier = []
output_offset = []
right_shift = []
output_scale = []
output_zero_point = []


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


x = 1
l1_input = int(x / 0.024574 - 128)

l1_results = []
l2_results = []

# Layer 1

for i in range(16):
    acc = (int(filter_vals[i]) + int(filter_offsets[i])) * (l1_input + int(input_offsets[i]))
    acc += int(bias_data[i])

    if acc > 0:
        acc = (acc * int(output_multiplier[i]) + 2**30) / 2**31
    else:
        acc = (acc * int(output_multiplier[i]) + (1 - 2**30)) / 2**31

    print(acc)

    acc = int(int(acc) / 2**int(right_shift[i]))

    print(acc)

    acc += int(output_offset[i])

    if acc < -128:
        acc = -128
    elif acc > 127:
        acc = 127

    l1_results.append(acc)

print(l1_results)

# Layer 2

for node in range(16):
    acc = 0
    for l1 in range(16):
        offset = 16 + (node*16) + l1
        acc += (int(filter_vals[offset]) + int(filter_offsets[offset])) * (l1_results[l1] + int(input_offsets[offset]))
    
    acc += int(bias_data[node+16])

    if acc > 0:
        acc = (acc * int(output_multiplier[node+16]) + 2**30) / 2**31
    else:
        acc = (acc * int(output_multiplier[node+16]) + (1 - 2**30)) / 2**31

    acc = int(int(acc) / 2**int(right_shift[node+16]))

    acc += int(output_offset[node+16])

    if acc < -128:
        acc = -128
    elif acc > 127:
        acc = 127

    l2_results.append(acc)

print(l2_results)

# Layer 3

acc = 0
for l2 in range(16):
    offset = 16 + (16*16) + l2
    acc += (int(filter_vals[offset]) + int(filter_offsets[offset])) * (l2_results[l2] + int(input_offsets[offset]))

acc += int(bias_data[32])

if acc > 0:
    acc = (acc * int(output_multiplier[32]) + 2**30) / 2**31
else:
    acc = (acc * int(output_multiplier[32]) + (1 - 2**30)) / 2**31

acc = int(int(acc) / 2**int(right_shift[32]))

acc += int(output_offset[32])

if acc < -128:
    acc = -128
elif acc > 127:
    acc = 127

print((acc - int(output_zero_point[0])) * float(output_scale[0]))
