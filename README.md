# BCC compiler

My implementation of of the compiler described in [Writing a C Compiler](https://nostarch.com/writing-c-compiler) by Nora Sandler.  
Targets the JPEB architecture

## Building

1. [Install ghcup](https://www.haskell.org/ghcup/install/)
2. `ghcup install ghc 9.4.8`
3. `ghcup set ghc 9.4.8`
4. `cabal build`

## Usage

Compiler flags: `tokens`, `ast`, `semantics`, `tac`, or `asm`. 
You can specify as many of these flags as you want, and the compiler will print
the output of the corresponding stage. 


Other flags: 
- `-out` if you want to keep the generated `.out` file
