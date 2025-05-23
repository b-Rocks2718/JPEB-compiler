import sys
import os
import argparse

valid_commands = ["add", "addi", "addc", "sub",
                  "subc", "and", "or", "xor",
                  "not", "shl", "shr", "rotl",
                  "rotr", "sshr", "shrc", "shlc",
                  "cmp", "nand", "lui", "sw", 
                  "lw", "jalr", "nop", "lli", 
                  "sys", "mov", "bz", "bne", "beq",
                  "bp", "bo", "bn", "bc", 
                  "bnz", "ba", "bae", "bb", "bbe", 
                  "movi", ".fill", ".space",
                  "jmp", "push", "pop",
                  "bnc", "call", 
                  "bg", "bge", "bl", "ble", "swi", "bno",]

macros = ["movi", ".fill", ".space", "push", "pop", "call", "swi"]

# types of instructions reg reg imm, reg reg reg, reg reg 
rri_type = ["addi", "sw", "lw"]
rrr_type = ["add", "addc", "and", "or", "xor", "nand"]
rr_type = ["not", "shl", "shr", "rotl",
           "rotr", "sshr", "shrc", "shlc"]

instruction_dict = {
    "add" : "000",
    "addi": "001",
    "addc": "000",
    "sub" : "000",
    "subc": "000",
    "and" : "000",
    "or"  : "000",
    "xor" : "000",
    "not" : "000",
    "shl" : "000",
    "shr" : "000",
    "rotl": "000",
    "rotr": "000",
    "sshr": "000",
    "shrc": "000",
    "shlc": "000",
    "cmp" : "000",
    "nand": "000",
    "lui" : "011",
    "sw"  : "100",
    "lw"  : "101",
    "jalr": "111",
    "nop" : "010",
    "lli" : "001",
    "sys" : "111",
    "mov" : "000",
    "bz"  : "110",
    "bp"  : "110",
    "bn"  : "110",
    "bc"  : "110",
    "bo"  : "110",
    "bnz" : "110",
    "bne" : "110",
    "beq" : "110",
    "jmp" : "110",
    "bnc" : "110",
    "bg"  : "110",
    "bge" : "110",
    "bl"  : "110",
    "ble" : "110",
    "ba"  : "110",
    "bae" : "110",
    "bb"  : "110",
    "bbe" : "110",
    "bno" : "110",
}

alu_dict = {
    "nand": "0000",
    "add" : "0001",
    "addc": "0010",
    "or"  : "0011",
    "subc": "0100",
    "and" : "0101",
    "sub" : "0110",
    "cmp" : "0110",
    "xor" : "0111",
    "not" : "1000",
    "shl" : "1001",
    "shr" : "1010",
    "rotl": "1011",
    "rotr": "1100",
    "sshr": "1101",
    "shrc": "1110",
    "shlc": "1111",
}

branch_dict = {
    "bz"  : "000000",
    "beq" : "000000",
    "bp"  : "000001",
    "bn"  : "000010",
    "bc"  : "000011",
    "bo"  : "000100",
    "bnz" : "000101",
    "bne" : "000101",
    "jmp" : "000110",
    "bnc" : "000111",
    "bg"  : "001000",
    "bge" : "001001",
    "bl"  : "001010",
    "ble" : "001011",
    "ba"  : "001100",
    "bae" : "001101",
    "bb"  : "001110",
    "bbe" : "001111",
    "bno" : "010000",
}

exception_dict = { 
    "EXIT": "1110000",
    # next exception will get code 1110001, then 1110010, ...
}

def get_imm(line_num, token, bits, side, labels, label_addresses, 
            address=-1, is_beq=0, is_movi=0):
    if token in labels:
        index = labels.index(token)
        if is_beq:
            assert address != -1, "That should not happen"
            n = label_addresses[index] - address - 1
        else:
            n = label_addresses[index]
    else:
        try:
            n = int(token, 0)
        except ValueError:
            assert False, f"Invalid immediate in line {line_num + 1}"
    assert bits < 17 and bits > 0, "That shouldn't happen"
    if is_movi:
        if n > 2 ** 16 - 1:
            print(f"Warning in line {line_num + 1}: out of bounds immediate")
    else:
        if side:
            if n > 2 ** 16 - 1 or n < -2 ** 15:
                print(f"Warning in line {line_num + 1}: out of bounds immediate")
        else:
            if n > 2 ** bits - 1 or n < - 2 ** (bits - 1):
                print(f"Warning in line {line_num + 1}: out of bounds immediate")
    if n < 0:
        n = -n
        n = ((2 ** 16 - 1) ^ n) + 1
    n = format(n, 'b').zfill(16)
    if side:
        return n[-16:bits - 16]
    else:
        return n[-bits:]

def num_bytes(tokens, line):
    assert tokens[0] in valid_commands, f"Unrecognized opcode: {tokens[0]}"
    if tokens[0] == ".space":
        assert len(tokens) == 2, f"Invalid use of .space in line {line}; correct usage is\".space <num_words>\""
        try:
            return int(tokens[1], 0)
        except ValueError:
            assert False, f"Invalid use of .space in line {line}; correct usage is\".space <num_words>\""
    elif tokens[0] in ["push", "pop", "movi"]:
        return 2
    elif tokens[0] in ["call", "swi"]:
        return 3
    else:
        return 1

def is_reg(token):
    if len(token) not in [2, 3]:
        return False
    if token[0] != 'r':
        return False
    if not token[1].isnumeric():
        return False
    if int(token[1]) not in range(8):
        return False
    if len(token) == 2:
        return True
    if len(token) == 3:
        if token[2] != ',':
            return False
    return True

def generate_opcode(line_num, tokens, labels, label_addresses, address):
    opcode = ""
    operation = tokens[0]
    assert operation in valid_commands, f"Unrecognized opcode in line {line_num + 1}: {operation}"
    if operation in instruction_dict:
        opcode += instruction_dict[operation]
        if operation == "lui":
            assert len(tokens) == 3, f"Error in line {line_num + 1}. RI type operation takes 2 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1], 0), 'b').zfill(3)
            opcode += get_imm(line_num, tokens[2], 10, 1, labels, label_addresses)
        elif operation == "jalr":
            assert len(tokens) == 3, f"Error in line {line_num + 1}. 'jalr' takes 2 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
            opcode += "0000000"
        elif operation in rri_type:
            assert len(tokens) == 4, f"Error in line {line_num + 1}. RRI type operation takes 3 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
            opcode += get_imm(line_num, tokens[3], 7, 0, labels, label_addresses, address, 0)
        elif operation in rrr_type:
            assert len(tokens) == 4, f"Error in line {line_num + 1}. RRR type operation takes 3 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[3]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
            opcode += alu_dict[operation]
            opcode += format(int(tokens[3][1]), 'b').zfill(3)
        elif operation in rr_type:
            assert len(tokens) == 3, f"Error in line {line_num + 1}. RR type operation takes 2 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += "000"
            opcode += alu_dict[operation]
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
        elif operation in branch_dict:
            assert len(tokens) == 2, f"Error in line {line_num + 1}. branch operation takes 1 parameter"
            opcode += branch_dict[operation]
            opcode += get_imm(line_num, tokens[1], 7, 0, labels, label_addresses, address, 1)
        elif operation == "nop":
            assert len(tokens) == 1, f"Error in line {line_num + 1}, nop takes no arguments"
            opcode += "0000000000000"
        elif operation == "clf":
            assert len(tokens) == 1, f"Error in line {line_num + 1}, clc takes no arguments"
            opcode += "0000000001000"
        elif operation == "lli":
            assert len(tokens) == 3, f"Error in line {line_num + 1}: 'lli' takes 2 arguments"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += ("0" + get_imm(line_num, tokens[2], 6, 0, labels, label_addresses))
        elif operation == "sys":
            assert len(tokens) == 2, f"Error in line {line_num + 1}: sys takes one argument"
            assert tokens[1] in exception_dict,  f"Error in line {line_num + 1}: unrecognized exception type"
            assert tokens[1][:3] != "INT", "Calling an INT results in an infinite loop"
            opcode += "000000"
            opcode += exception_dict[tokens[1]]
        elif operation == "mov":
            assert len(tokens) == 3, f"Error in line {line_num + 1}: 'mov' takes 2 arguments"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += "0000001"
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
        elif operation == "cmp":
            assert len(tokens) == 3, f"Error in line {line_num + 1}: 'cmp' takes 2 arguments"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            opcode += "000"
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
            opcode += alu_dict["cmp"]
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
        elif operation == "sub" or operation == "subc":
            assert len(tokens) == 4, f"Error in line {line_num + 1}: 'sub' takes 3 arguments"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[3]), f"Error in line {line_num + 1}: Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += format(int(tokens[3][1]), 'b').zfill(3)
            opcode += alu_dict[operation]
            opcode += format(int(tokens[2][1]), 'b').zfill(3)
        else:
            raise BaseException(f"AssemblerError - {operation} has no machine code definition")
    elif operation in macros:
        if operation == "movi":
            opcode += "011"
            assert len(tokens) == 3, f"Error in line {line_num + 1}. movi type operation takes 2 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1], 0), 'b').zfill(3)
            opcode += get_imm(line_num, tokens[2], 10, 1, labels, label_addresses, is_movi=1)
            opcode = hex(int(opcode, 2))[2:].zfill(4) + '\n'
            
            opcode2 = "001"
            opcode2 += format(int(tokens[1][1]), 'b').zfill(3)
            opcode2 += format(int(tokens[1][1]), 'b').zfill(3)
            opcode2 += ("0" + get_imm(line_num, tokens[2], 6, 0, labels, label_addresses, is_movi=1))
            opcode2 = hex(int(opcode2, 2))[2:].zfill(4) + '\n'
            return opcode + opcode2
        elif operation == ".fill":
            assert len(tokens) == 2, f"Error in line {line_num + 1}: .fill takes one argument"
            opcode += get_imm(line_num, tokens[1], 16, 0, labels, label_addresses)
        elif operation == ".space":
            # TODO: test this, might be buggy
            assert len(tokens) == 2, f"Error in line {line_num + 1}: .space takes one argument"
            assert tokens[1].isnumeric(), f"Error in line {line_num + 1}: .space takes an integer argument"
            n = int(tokens[1])
            opcode = ""
            for _ in range(n):
                opcode += "0000\n"
            return opcode
        elif operation == "push":
            # dec sp, then store
            assert len(tokens) == 2, f"Error in line {line_num + 1}: push takes one argument"
            temp    = hex(int("0010010011111111", 2))[2:].zfill(4) + '\n'
            opcode += "100" 
            opcode += format(int(tokens[1][1]), 'b').zfill(3)
            opcode += "0010000000"
            opcode =  temp + hex(int(opcode, 2))[2:].zfill(4) + '\n'
            return opcode
        elif operation == "pop":
            # load, then inc sp
            assert len(tokens) == 2, f"Error in line {line_num + 1}: pop takes one argument"
            temp = "101"
            temp += format(int(tokens[1][1]), 'b').zfill(3)
            temp += "0010000000"
            opcode += hex(int(temp, 2))[2:].zfill(4) + '\n'
            opcode += hex(int("0010010010000001", 2))[2:].zfill(4) + '\n'
            return opcode
        elif operation == "call":
            assert len(tokens) == 2, f"Error in line {line_num + 1}: call takes one argument"
            # convert to: 
            # movi r7 <value>
            # jalr r7 r7
            opcode += "011"
            opcode += "111"
            opcode += get_imm(line_num, tokens[1], 10, 1, labels, label_addresses, is_movi=1)
            opcode = hex(int(opcode, 2))[2:].zfill(4) + '\n'
            
            opcode2 = "001"
            opcode2 += "111111"
            opcode2 += ("0" + get_imm(line_num, tokens[1], 6, 0, labels, label_addresses, is_movi=1))
            opcode2 = hex(int(opcode2, 2))[2:].zfill(4) + '\n'
            
            opcode3 = "1111111110000000"
            opcode3 = hex(int(opcode3, 2))[2:].zfill(4) + '\n'
            return opcode + opcode2 + opcode3
        elif operation == "swi": 
            # swi  rA rB <value>
            # convert to:
            # movi rA <value>
            # sw   rA rB
            opcode += "011"
            assert len(tokens) == 4, f"Error in line {line_num + 1}. swi type operation takes 3 parameters"
            assert is_reg(tokens[1]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            assert is_reg(tokens[2]), f"Error in line {line_num + 1}. Valid register names are r0, r1, ..., r7"
            opcode += format(int(tokens[1][1], 0), 'b').zfill(3)
            opcode += get_imm(line_num, tokens[3], 10, 1, labels, label_addresses, is_movi=1)
            opcode = hex(int(opcode, 2))[2:].zfill(4) + '\n'
            
            opcode2 = "001"
            opcode2 += format(int(tokens[1][1]), 'b').zfill(3)
            opcode2 += format(int(tokens[1][1]), 'b').zfill(3)
            opcode2 += ("0" + get_imm(line_num, tokens[3], 6, 0, labels, label_addresses, is_movi=1))
            opcode2 = hex(int(opcode2, 2))[2:].zfill(4) + '\n'
            
            opcode3 = "100"
            opcode3 += format(int(tokens[1][1]), 'b').zfill(3)
            opcode3 += format(int(tokens[2][1]), 'b').zfill(3)
            opcode3 += "0000000"
            opcode3 = hex(int(opcode3, 2))[2:].zfill(4) + '\n'
            return opcode + opcode2 + opcode3
        else:
            raise BaseException(f"Macro '{operation}' has no definition")
    else:
        raise BaseException("you really messed up this time")
    
    if opcode != "":
        opcode = hex(int(opcode, 2))[2:].zfill(4) + '\n'
    return opcode

def assemble(args, tracked_labels):
    address = 0
    data = []
    for name in args.inputs:
        input_file = open(name, 'r')
        data += input_file.readlines()
        input_file.close()
    
    # first pass: convert labels to addresses
    labels = []
    label_addresses = []
    address = 0

    for line_num, line in enumerate(data):
        line = line.replace("\n", "")
        line = line.replace("\t", " ")
        if '#' in line:
            # remove comments
            index = line.index('#')
            line = line[:index - 1]
        tokens = line.split(" ")
        while "" in tokens:
            tokens.remove("")
        if tokens != []:
            if tokens[0] not in valid_commands:
                if tokens[0][-1] == ':':
                    # this is a label
                    assert tokens[0][:-1] not in labels, f"Repeated label: {tokens[0][:-1]}"
                    labels.append(tokens[0][:-1])
                    label_addresses.append(address)
                    if len(tokens) != 1:
                        # there's an opcode on the same line
                        address += num_bytes(tokens[1:], line_num + 1)
                elif tokens[0][0] == '#':
                    # this is a comment
                    pass
                else:
                    assert False, f"Unrecognized opcode in line {line_num + 1}: {tokens[0]}"
            else:
                address += num_bytes(tokens, line_num + 1)
    # second pass: generate machine code
    file_lines = []
    address = 0
    for line_num, line in enumerate(data):
        line = line.replace("\n", "")
        line = line.replace("\t", " ")
        if '#' in line:
            # remove comments
            index = line.index('#')
            line = line[:index - 1]
        opcode = ""
        tokens = line.split(" ")
        while "" in tokens:
            tokens.remove("")
        if tokens != []:
            if tokens[0][0] == '#':
                continue
            if tokens[0][:-1] in labels and tokens[0][:-1] == ':':
                opcode = generate_opcode(line_num, tokens[1:], labels, label_addresses, address)
                address += num_bytes(tokens, line_num + 1)
            elif len(tokens) != 1:
                opcode = generate_opcode(line_num, tokens, labels, label_addresses, address)
                address += num_bytes(tokens, line_num + 1)
            if opcode != "":
                file_lines.append(opcode)

    f = open(f"{args.output}.hex", 'w')
    for line in file_lines:
        f.write(line)
    f.close()
    for label, address in zip(labels, label_addresses):
        if label in tracked_labels:
            print(f"{label}: {address} = {hex(address)}")

# names[0] is main
# names[1:] are libraries to include       
def assemble_to_binary(args, tracked_labels = []):

    bytes_list = []
    
    # generate machine code file
    assemble(args, tracked_labels)
    
    # open file
    input_file = open(args.output + ".hex", 'r')

    f = open(args.output + '.bin', 'wb')

    for line in input_file.readlines():
        value = int(line, 16)
        upper_byte = value & 0b1111_1111_0000_0000
        upper_byte = upper_byte >> 8
        lower_byte = value & 0b0000_0000_1111_1111
        bytes_list.append(lower_byte)
        bytes_list.append(upper_byte)

    f.write(bytes(bytes_list))
    # close files
    input_file.close()
    f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description ='Assemble to JPEB bin')
    parser.add_argument(
        'inputs',
        nargs='+',
        help='Files to assemble'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Path to output to',
        default=None
    )
    args = parser.parse_args()

    if args.output is None:
        parts = args.inputs[0].split('.')[:-1]
        args.output = '.'.join(parts)
    else:
        args.output += '/' + args.inputs[0].split('/')[-1].split('.')[0]

    assemble_to_binary(args)
