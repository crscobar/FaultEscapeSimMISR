from yachalk import chalk

# Class used to store information for a wire
class Node(object):
    def __init__(self, name, value, gatetype, innames, gateinput, fgate, fgateSA):
        self.name = name  # string
        self.value = value  # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype  # string such as "AND", "OR" etc
        self.interms = []  # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False  # boolean: true if this wire is a primary input of the circuit
        self.is_output = False  # boolean: true if this wire is a primary output of the circuit
        self.gateinput = gateinput # the input for the gates
        self.fgate = ""   # Faulty input into gate
        self.fgateSA = "-1"   # Fault type
        
    def set_value(self, v):
        self.value = v

    def display(self):  # print out the node nicely on one line

        if self.is_input:
            # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}"
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
            print(nodeinfo)
            return
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:  # internal nodes
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name) + " "
            interm_val_str += str(i.value) + " "

        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"

        print(nodeinfo)
        return

        # calculates the value of a node based on its gate type and values at interms

    def calculate_value(self):
        count0 = 0
        count1 = 0
        countU = 0
        
        # - If there is a fault over gate, modifiy calucation to account for failure
        # duplicate interms localy to not effect other calcuations
        input_values = []
        for current_input in self.interms:
            if self.fgate == current_input.name:
                input_values.append(self.fgateSA)
            else:
                input_values.append(current_input.value)

        #done
        if self.gatetype == "AND":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count0 > 0:
                    val = "0"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "1"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val
        #done
        elif self.gatetype == "OR":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "1"
                if count1 == 0 and countU > 0:
                    val = "U"
                if count0 > 0 and count1 == 0 and countU == 0:
                    val = "0"
            self.value = val
            return val
        #done
        elif self.gatetype == "NAND":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count0 > 0:
                    val = "1"
                if count0 == 0 and count1 == 0:
                    val = "U"
                if count0 == 0 and countU == 0:
                    val = "0"
                if count0 == 0 and count1 > 0 and countU > 0:
                    val = "U"
            self.value = val
            return val
        #done
        elif self.gatetype == "NOT":
            for i in input_values:
                if i == "U":
                    val = "U"
                    return val
                else:
                    val = input_values[0]
                    self.value = str(1-int(val))
                    return val
            self.value = val
            return val
        #done
        elif self.gatetype == "XOR":
            for i in input_values:
                if i == "U":
                    countU += 1
                    val = "U"
                    return val
                elif i == "0":
                    count0 += 1
                    val = count0 % 2
                    val = str(val)
                elif i == "1":
                    count1 += 1
                    val = count1 % 2
                    val = str(val)
            self.value = val
            return val 
        #done
        elif self.gatetype == "XNOR":
            for i in input_values:
                if i == "U":
                    count1 += 1
                    val = "U"
                    return val
                elif i == "0":
                    count0 += 1
                    output = count0 % 2
                    val = str(1-output)   
                elif i == "1":
                    count1 += 1
                    val = count1 % 2
                    val = str(1- val)
            self.value = val
            return val
        #done
        elif self.gatetype == "NOR":
            for i in input_values:
                if i == "0":
                    count0 += 1
                if i == "U":
                    countU += 1
                if i == "1":
                    count1 += 1
                if count1 > 0:  # 1 ORed with anything is a 1
                    val = "0"
                elif count1 == 0 and countU > 0:
                    val = "U"
                elif count0 > 0 and count1 == 0 and countU == 0:
                    val = "1"
            self.value = val
            return val
        #done
        elif self.gatetype == "BUFF":
            val = input_values[0]
            self.value = val
            return val
        #done
        elif self.gatetype == "DFF":  
            val = input_values[0]
            self.value = val
            return val

# Take a line from the circuit file which represents a gatetype operation and returns a node that stores the gatetype
def parse_gate(rawline):
    # example rawline is: a' = NAND(b', 256, c')
    # should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

    # get rid of all spaces
    line = rawline.replace(" ", "")

    name_end_idx = line.find("=")
    node_name = line[0:name_end_idx]

    gt_start_idx = line.find("=") + 1
    gt_end_idx = line.find("(")
    node_gatetype = line[gt_start_idx:gt_end_idx]

    # get the string of interms between () to build tp_list
    interm_start_idx = line.find("(") + 1
    end_position = line.find(")")
    temp_str = line[interm_start_idx:end_position]
    tp_list = temp_str.split(",")

    node_innames = [i for i in tp_list]

    return node_name, node_gatetype, node_innames


# Create circuit node list from input file
def construct_nodelist():
    o_name_list = []
    gateinput = None
    for line in input_file_values:
        if line == "\n":
            continue

        if line.startswith("#"):
            continue

        if line.startswith("INPUT"):
            index = line.find(")")
            name = str(line[6:index])
            n = Node(name, "U", "PI", [], gateinput, '', -1)
            n.is_input = True
            node_list.append(n)

        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)

        elif line.startswith("DFF"):
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "0", node_gatetype, node_innames, gateinput, '', -1)
            node_list.append(n)

        else:  # majority of internal gates processed here
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "U", node_gatetype, node_innames, gateinput, '', -1)
            node_list.append(n)

    # now mark all the gates that are output as is_output
    for n in node_list:
        if n.name in o_name_list:
            n.is_output = True

    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    for node in node_list:
        for cur_name in node.innames:
            for target_node in node_list:
                if target_node.name == cur_name:
                    node.interms.append(target_node)
                    
    return


# TODO: make a circuit class, containing a nodelist, display function, and simulation method. (Rao)
# Helper Function # My Code Signory Somsavath
def remove_dup(x):
    i = 0 
    while i < len(x):
        j = i +1
        while j < len(x):
            if x[i] == x[j]:
                del x[j]
            else:
                j+=1
        i += 1

def test_vectors():
    numberOfInputs = []
    vecLst = []
    for node in node_list:
       if (node.is_input):
           numberOfInputs.append(node.name)
           remove_dup(numberOfInputs)
    #print(numberOfInputs)
    total = 2**(len(numberOfInputs))
    while (total != -1):
        z = bin(total)[2:].zfill(numInputNodes)
        total += -1
        vecLst.insert(0, z)
    vecLst.pop()
    return vecLst

def full_coverage():
    gateList = [] #Gates Inputs for example g-'a'-1 or g-'b'-1
    outputGate = [] # Names of the Gate output 'g'-a-1 
    allInputs = []
    faultLst = []
    i = 0
    j = 0
    k = 0
    for node in node_list:
        allInputs.append(node.name)
        for gateInput in node.innames:
            for target in node_list:
                if target.name == gateInput:
                    gateList.append(node.innames)
                    outputGate.append(node.name)
    while ( j < len(allInputs)):
            a = ("{}-{}".format(allInputs[j],0))
            b = ("{}-{}".format(allInputs[j],1))
            faultLst.append(a),faultLst.append(b)
            j += 1
    while (i < len(outputGate)):
        k = 0
        while (k < len(gateList[i])):
            a = ("{}-{}-0".format(outputGate[i],gateList[i][k]))
            b = ("{}-{}-1".format(outputGate[i],gateList[i][k]))
            faultLst.append(a),faultLst.append(b)
            k += 1
        i +=1    
    remove_dup(faultLst)
    return faultLst

# this function will add a fault into our circuit after being constructed
def addFaultAt(x):

    parsed_list = []

    parsed_list = x.split("-")

    strindex = 0

    for node in node_list:
        #print("{} vs {}".format(node.name, parsed_list[0]))
        if node.name == parsed_list[0]:
            if len(parsed_list) == 2:
                node.value = parsed_list[1]

            else:
                node.fgate = parsed_list[1]   
                node.fgateSA = parsed_list[2]   
            
            if node.is_input:
                strindex = strindex + 1

        elif node.is_input:
            node.set_value(current_vector[strindex])
            strindex = strindex + 1

    return

# using this to clone a list for a fault
def cloneList(nlist):
    fnode_list = nlist[:]
    return fnode_list


def D_Two_A(originalSeed):  # 8-bit LFSRs with no taps (shifter)
    seedChunk = originalSeed
    newSeed = ''
    #print("\n\nSEED CHUNK: {}".format(seedChunk))
    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += seedChunk[1]
    newSeed += seedChunk[2]
    newSeed += seedChunk[3]
    newSeed += seedChunk[4]
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]

    return newSeed

def D_Two_B(originalSeed):  # 8-bit LFSRs with taps at 2, 4, 5
    seedChunk = originalSeed
    newSeed = ''
    #print("\n\nSEED CHUNK: {}".format(seedChunk))
    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += str(ord(seedChunk[1]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[2]
    newSeed += str(ord(seedChunk[3]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[4]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]

    return newSeed  

def D_Two_C(originalSeed):  # 8-bit LFSRs with taps at 2, 3, 4
    seedChunk = originalSeed
    newSeed = ''
    #print("\n\nSEED CHUNK: {}".format(seedChunk))
    newSeed += seedChunk[7]     
    newSeed += seedChunk[0]
    newSeed += str(ord(seedChunk[1]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[2]) ^ ord(seedChunk[7]))
    newSeed += str(ord(seedChunk[3]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[4]
    newSeed += seedChunk[5]
    newSeed += seedChunk[6]

    return newSeed

def D_Two_D(originalSeed):  # 8-bit LFSRs with taps at 3, 5, 7
    seedChunk = originalSeed
    newSeed = ''
    newSeed += seedChunk[7]
    newSeed += seedChunk[0]
    newSeed += seedChunk[1]
    newSeed += str(ord(seedChunk[2]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[3]
    newSeed += str(ord(seedChunk[4]) ^ ord(seedChunk[7]))
    newSeed += seedChunk[5]
    newSeed += str(ord(seedChunk[6]) ^ ord(seedChunk[7]))

    return newSeed

def misr_good_output(output_list):
    seed = "0"
    seed = seed.zfill(numOutputNodes)

    counter = 1
    xor_out = ""
    xor_list = []
    
    for output in output_list:
        if counter != 1:
            temp = xor_out
        else:
            temp = seed
        xor_out = ""

        for i in range(len(output)):
            xor_out += str(ord(output[i]) ^ ord(temp[i]))

        counter += 1
        if len(xor_out) < numOutputNodes:
            xor_out = xor_out.zfill(numOutputNodes)
        #print("{} XOR {} = {}\n".format(output, temp, xor_out))

        xor_list.append(xor_out)

    return xor_list

def misr_bad_output(output_list_list):
    seed = "0"
    seed = seed.zfill(numOutputNodes)

    
    xor_out = ""
    xor_list_list = []
    loop = 1
    for output_list in output_list_list:
        counter = 1
        xor_list = []

        for output in output_list:
            if counter != 1:
                temp = xor_out
            else:
                temp = seed
            xor_out = ""  

            for i in range(len(output)):
                xor_out += str(ord(output[i]) ^ ord(temp[i]))

            counter += 1
            if len(xor_out) < numOutputNodes:
                xor_out = xor_out.zfill(numOutputNodes)
            #print("{} XOR {} = {}\n".format(output, temp, xor_out))

            xor_list.append(xor_out)
        #print("Finished loop {}".format(loop))
        #print(xor_list)
        loop += 1
        xor_list_list.append(xor_list)

    return xor_list_list

def listToString(s):  
    # initialize an empty string 
    str1 = ""  

    # traverse in the string   
    for ele in s:  
        str1 += ele   
    
    # return string   
    return str1 

# Main function starts

# Step 1: get circuit file name from command line
print(chalk.yellow("*********************************************************************************************************"))
print(chalk.yellow('* ___  ________ ___________  ______          _ _     _____                           _____ _            *'))
print(chalk.yellow('* |  \/  |_   _/  ___| ___ \ |  ___|        | | |   |  ___|                         /  ___(_)           *'))
print(chalk.yellow('* | .  . | | | \ `--.| |_/ / | |_ __ _ _   _| | |_  | |__ ___  ___ __ _ _ __   ___  \ `--. _ _ __ ___   *'))
print(chalk.yellow("* | |\/| | | |  `--. \    /  |  _/ _` | | | | | __| |  __/ __|/ __/ _` | '_ \ / _ \  `--. \ | '_ ` _ \  *"))
print(chalk.yellow('* | |  | |_| |_/\__/ / |\ \  | || (_| | |_| | | |_  | |__\__ \ (_| (_| | |_) |  __/ /\__/ / | | | | | | *'))
print(chalk.yellow('* \_|  |_/\___/\____/\_| \_| \_| \__,_|\__,_|_|\__| \____/___/\___\__,_| .__/ \___| \____/|_|_| |_| |_| *'))
print(chalk.yellow('*                                                                      | |                              *'))
print(chalk.yellow('*                                                                      |_|                              *'))
print(chalk.yellow('*********************************************************************************************************\n'))

wantToInputCircuitFile = str(
    input(chalk.green("Provide a benchfile name (return to accept 's208.bench' by default):\n")))

if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
        f = open(circuitFile)
        f.close()
    except FileNotFoundError:
        print('File does not exist, setting circuit file to default')
        circuitFile = "s208.bench"
else:
    circuitFile = "s208.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
node_list = []
construct_nodelist()
# printing list of constructed nodes

dff_list = []

for node in node_list:
    if node.gatetype == "DFF":
        dff_list.append(node.name)
        #print("Added {}".format(node.name))

for node in node_list:
    for term in node.interms:
        #print("{}-{}, {} = {}".format(node.name, term.name, term.name, term.value))
        for dff in dff_list:
            if dff == term.name:
                term.value = "0"
        

display_choice = input(chalk.green("\nShow initial node list? (yes or no)\n"))
if (display_choice[0].lower() == 'y'):
    for n in node_list:
        n.display()

# Bookeeping
total_fault_list = []

# Bookeep the number of inputs
numInputNodes = 0
for node in node_list:
    if node.is_input:
        numInputNodes += 1

numOutputNodes = 0
for node in node_list:
    if node.is_output:
        numOutputNodes += 1

# Produce full fault list for the ciruit 
fault_list = full_coverage()

choice = input(chalk.green("\nShow every fault possible? (yes or no)\n"))

print("\n----------------------------------------------------\n")

if choice[0].lower() == "y":
    print("")
    for fault in fault_list:
        print("{}, ".format(fault), end="")
    print("\n")

while True:
    tv_list = []

    # -- Circuit input handling 
    # -- More than 6 inputs
    if(numInputNodes > 6):
        operation_choice = input(chalk.green("Which LFSR would you like to run?\n") + "\t(a) 8-bit LFSRs with no taps (shifter) " + 
            "\n\t(b) 8-bit LFSRs with taps at 2, 4, 5\n\t(c) 8-bit LFSRs with taps at 2, 3, 4 " +
            "\n\t(d) 8-bit LFSRs with taps at 3, 5, 7\n\t(e) n-bit Counter\n\t(f) Quit\n\n\t")
  
        if(ord(operation_choice.lower()) < 97 or ord(operation_choice.lower()) > 102):
            operation_choice = input("Invalid choice, choose one of the following:\n\t(a) 8-bit LFSRs with no taps (shifter) " + 
            "\n\t(b) 8-bit LFSRs with taps at 2, 4, 5\n\t(c) 8-bit LFSRs with taps at 2, 3, 4 " +
            "\n\t(d) 8-bit LFSRs with taps at 3, 5, 7\n\t(e) n-bit Counter\n\t(f) Quit\n\n\t")

        if(operation_choice.lower() == 'f'.lower()):
            print("Bye!")
            exit()

        hexNum = input(chalk.green("\nEnter an 8-byte LFSR hex seed number (start with 0x...):\n"))

        binString = ''
        hexNumLen = len(hexNum) - 2
        binNum = bin(int(hexNum, 16))
        binNum = binNum[2:]
        totalLen = (hexNumLen) * 4

        if len(binNum) < totalLen:
            binNum = binNum.zfill(totalLen)

        print("\nThe binary TV generated from seed is: {}".format(binNum))

        if len(binNum) < numInputNodes:
            while(len(binNum) < numInputNodes):
                binNum += binNum
        if len(binNum) > numInputNodes:
            binNum = binNum[0:numInputNodes]
            print("Since binary TV length is greater than number of PIs, applied seed is: {}\n".format(binNum))

        loops = min(100, 2**numInputNodes)

        misr_seeds = []

        if(operation_choice.lower() != 'e'.lower()):
            misr_choice = input(chalk.green("Do you want to find the fault escape rate of MISR? (yes or no):\n"))
                
        # -- LFSR calcuations
        # -- Now using input test vector to generate next vectors with select LFSR
        x = int(binNum, 2)

        # -- 8-bit LFSRs with no taps (shifter)
        if(operation_choice.lower() == 'a'.lower()):
            # -- Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)

            tv_list.append(prior_test_vector)

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                lfsr_test_vector = ""
                
                # -- Generate full string of vector
                for j in range(int(len(prior_test_vector) / 8)):
                    lfsr_test_vector = lfsr_test_vector + D_Two_A(prior_test_vector[j*8:(j+1)*8])
                
                # -- If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector) % 8 != 0:     # FIX
                    # Run LFSR with extra zeros to compenstate for lack of input
                    lfsr_full_content = D_Two_A(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector) % 8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    lfsr_test_vector = lfsr_test_vector + lfsr_full_content[0:len(prior_test_vector) % 8]

                prior_test_vector = lfsr_test_vector

                tv_list.append(lfsr_test_vector)
        
        # -- 8-bit LFSRs with taps at 2, 4, 5 
        elif(operation_choice.lower() == 'b'.lower()):
            # -- Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)

            tv_list.append(prior_test_vector)
            # -- Create full batch of test vectors
            for i in range(0,loops-1): 
                lfsr_test_vector = ""
                
                # -- Generate full string of vector
                for j in range(int(len(prior_test_vector) / 8)):
                    lfsr_test_vector = lfsr_test_vector + D_Two_B(prior_test_vector[j*8:(j+1)*8])
                
                # -- If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector) % 8 != 0:     # FIX
                    # Run LFSR with extra zeros to compenstate for lack of input
                    lfsr_full_content = D_Two_B(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector) % 8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    lfsr_test_vector = lfsr_test_vector + lfsr_full_content[0:len(prior_test_vector) % 8]

                prior_test_vector = lfsr_test_vector

                tv_list.append(lfsr_test_vector)

        # -- 8-bit LFSRs with taps at 2, 3, 4
        elif(operation_choice.lower() == 'c'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)

            tv_list.append(prior_test_vector)
            #print("LFSR Vector List: {}".format(tv_list))

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                lfsr_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector) / 8)):
                    lfsr_test_vector = lfsr_test_vector + D_Two_C(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector) % 8 != 0:     # FIX
                    # Run LFSR with extra zeros to compenstate for lack of input
                    lfsr_full_content = D_Two_C(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector) % 8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    lfsr_test_vector = lfsr_test_vector + lfsr_full_content[0:len(prior_test_vector) % 8]

                prior_test_vector = lfsr_test_vector

                tv_list.append(lfsr_test_vector)

        # -- 8-bit LFSRs with taps at 3, 5, 7 
        elif(operation_choice.lower() == 'd'.lower()):
            # - Initial TV
            prior_test_vector = bin(x)[2:].zfill(numInputNodes)

            tv_list.append(prior_test_vector)
            #print("LFSR Vector List: {}".format(tv_list))

            # Create full batch of test vectors
            for i in range(0,loops-1): 
                lfsr_test_vector = ""
                
                # - Generate full string of vector
                for j in range(int(len(prior_test_vector) / 8)):
                    lfsr_test_vector = lfsr_test_vector + D_Two_D(prior_test_vector[j*8:(j+1)*8])
                
                # - If length does not match evenly with 8 input, last one uses less inputs
                if len(prior_test_vector) % 8 != 0:     # FIX
                    # Run LFSR with extra zeros to compenstate for lack of input
                    lfsr_full_content = D_Two_D(prior_test_vector[(len(prior_test_vector) - len(prior_test_vector) % 8):(len(prior_test_vector))].zfill(8))
                    
                    # pinch off what is not needed for TV
                    lfsr_test_vector = lfsr_test_vector + lfsr_full_content[0:len(prior_test_vector) % 8]

                prior_test_vector = lfsr_test_vector

                tv_list.append(lfsr_test_vector)
               
        # -- N-bit counter
        elif(operation_choice.lower() == 'e'.lower()): 
            # Create full batch of test vectors
            for i in range(loops):
                # To account for overflow, reset TV back to zero
                if(x == 2**hexNumLen):
                    x = 0
                # Generate test vector and add to list
                binString = bin(x)[2:].zfill(numInputNodes)
                tv_list.append(binString)

                # Increment TV by 1
                x += 1

        else:
            print("No idea how you got here, don't do it again pls :)")
            exit()

        # - Option for less clutered output when getting accumulative fault coverage
        # - First loop run setup
        vector_list = tv_list[0 : 10]
        
            # add MISR part

        # Bookeeping
        lfsr_history_per = []
        proc = 10
        cur_runs = 1

    # -- less than 7 input 
    # Will run all TV and and show information related to TV 
    else:
        input("\nHit enter to start operation")
        vector_list = test_vectors()
        
      
    print("\n")
    
    loop = 0
    detected_fault_list = []
    good_resp = []
    bad_resp = []
    dff_names = []

    for current_vector in tv_list:
        #print("TV {}({})\n".format(current_vector, loop))
        good_output_val = []
        curr_vec = []
        vec_faults = []
        # --- Good circuit run
        # - Clear all nodes values to U in between simulation runs
        for node in node_list:
            node.set_value("U")
            node.fgate = ''
            node.fgateSA = -1

        strindex = 0
        # - Set value of input node
        for node in node_list:
            if node.is_input:
                if strindex > len(current_vector)-1:
                    break
                node.set_value(current_vector[strindex])
                strindex = strindex + 1       

        # --- Simulate by calculating each node's values
        # - Initialize updated_count to 1 to enter while loop at least once
        updated_count = 1
        updated_output = 0
        iteration = 0

        while updated_output != numOutputNodes:
            updated_count = 0
            updated_output = 0  

            iteration += 1

            for n in node_list:

                if iteration == 1:
                    for term in n.interms:
                        #print("{}-{}, {} = {}".format(node.name, term.name, term.name, term.value))
                        for dff in dff_list:
                            if dff == term.name:
                                term.value = "0"

                if n.value == "U":
                    n.calculate_value()
                    if n.value == "0" or n.value == "1":
                        updated_count +=1
                
                if n.is_output:
                    if n.value ==  "0" or n.value ==  "1":
                        updated_output += 1

                else:
                    n.calculate_value()

        good_output_val = [i.value for i in node_list if i.is_output]
        good_resp.append(listToString(good_output_val))

        # --- Bad circuits
        # -- Running through each fault to see if issue detected
        current_vector_fault_list = []
        bad_output_list = []

        for current_fault in fault_list:
            # Clean nodes before start sim
            for node in node_list:
                node.set_value("U")
                node.fgate = ''
                node.fgateSA = -1

            addFaultAt(current_fault)      
                           
            # --- Simulate by calculating each node's values
            # - Initialize updated_count to 1 to enter while loop at least once
            updated_count = 1
            iteration = 0

            while updated_count > 0:
                updated_count = 0
                iteration += 1
                for n in node_list:

                    if iteration == 1:
                        for term in n.interms:
                            for dff in dff_list:
                                if dff == term.name:
                                    term.value = "0"

                    if n.value == "U":
                        n.calculate_value()
                        if n.value == "0" or n.value == "1":
                            updated_count +=1

            bad_output_val = [i.value for i in node_list if i.is_output]
            bad_output_list.append(listToString(bad_output_val))

            # --- Simulation results
            # - Locating if there is delta on output
            faulty_nodes = 0
            for i in range(len(good_output_val)):
                # Recording outputs that show faulty event
                if(good_output_val[i] != bad_output_val[i]):
                    faulty_nodes = 1
            
            # - Determining if fault is detected
            if not(faulty_nodes == 0):
                current_vector_fault_list.append(current_fault)
                
        bad_resp.append(bad_output_list)

        print_detected_fault = "{}".format(current_vector)
        for cur_fault in current_vector_fault_list:
            print_detected_fault = print_detected_fault + ",{}".format(cur_fault)
        
        # --- Test vector Results
        # - Parsing out vector and associated faults
        print_detected_fault = "{}".format(current_vector)
        for cur_fault in current_vector_fault_list:
            print_detected_fault = print_detected_fault + ",{}".format(cur_fault)
        # - Store result in to csv file
        detected_fault_list.append(print_detected_fault)

        loop += 1
        loadBar = "Calculating w/ TV " + current_vector + " : [" + "-" * loop + ">" + " " * (len(tv_list) - loop) + "]"
        if (loop % 4 == 0):
            print(loadBar, end="\r")
    print(chalk.yellow_bright("\nCalculation Complete!\n"))


    print(chalk.cyan("\n\nMISR Calculations"))
    good_sig = []
    good_sig = misr_good_output(good_resp)

    bad_sig = []
    bad_sig = misr_bad_output(bad_resp)

    print("Finding Fault Escape Rate")

    fault_escape = 0
    fault_detected = 0
    fault_escape_rate = 0
    fault_not_detected = 0
    loop = 1

    if(numInputNodes > 6):
        for i in range(len(good_resp)):
            for j in range(len(bad_resp[i])):
                if(good_resp[i] != bad_resp[i][j] and good_sig[i] == bad_sig[i][j]):
                    fault_escape += 1

                if(good_resp[i] != bad_resp[i][j] and good_sig[i] != bad_sig[i][j]):
                    fault_detected += 1

                if(good_resp[i] == bad_resp[i][j]):
                    fault_not_detected += 1        
        fault_escape_rate = (fault_escape / (fault_detected + fault_not_detected + fault_escape)) * 100

        print(chalk.magenta("Fault Escape Rate is using option ({}): ").format(operation_choice), end='')
        print("{}%\n\n".format(fault_escape_rate))
        input()
    else:
        print("\nFor some reason that I can't figure out, circuits with 6 or less PIs doesn't work, sorry :')\n")
        input()
        exit()