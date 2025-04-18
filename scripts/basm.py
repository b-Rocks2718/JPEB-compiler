import sys
import os

flags = [
    "-out"
]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: basm <file.s> <flags>")
        sys.exit(1)

    args = sys.argv[2:]

    asmfile = sys.argv[1]
    name = asmfile.split('.')[0]
    outfile = name + ".out"
    binfile = name + ".bin"

    assembler_args = []
    for arg in args:
        # separate flags
        if arg in flags:
            assembler_args.append(arg)
        else:
            print("Unrecognized flag: " + arg)
            print("Valid flags are:")
            print("-out")
            sys.exit(1)

    # run the assembler, exit if it fails
    if os.system("python3 Assembler.py " + asmfile + 
          ' asm_libraries/arithmetic.s ' + 
          ' '.join(assembler_args)):
        # exit if nonzero error code
        sys.exit(1)
    if not os.path.exists(binfile):
       sys.exit(1)
    
    if "-out" not in args:
        # remove .out files
        os.system("rm " + outfile)
    
