# BCC compiler

My implementation of of the compiler described in [Writing a C Compiler](https://nostarch.com/writing-c-compiler) by Nora Sandler.  
Targets the JPEB architecture

## Usage

Run 
```bash
source scripts/bcc.sh
```
from the `c-compiler` directory to be able to use the following commands. 

Compile with

```bash
bcc source.c -flags
```
Compiler flags: `tokens`, `ast`, `semantics`, `tac`, or `asm`. 
You can specify as many of these flags as you want, and the compiler will print
the output of the corresponding stage. 

Assembler flags: `-emu` if you want to target the emulator. The Digital simulation is targeted by default, and the output is written to the folder with the cpu simulation.

Other flags: 
- `-out` if you want to keep the generated `.out` file

You can also run 
```bash
basm source.s
```
to assemble an assembly file. `basm` accepts the `-emu`, `-run`, `-s`, `-out`, and `-bin` flags.

Run the emulator with 
```bash
bemu source.bin
```