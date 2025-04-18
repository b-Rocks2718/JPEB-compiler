	movi r3 main
	jalr r0  r3 

# Data Section:
hello:
	.fill 72
	.fill 101
	.fill 108
	.fill 108
	.fill 111
	.fill 32
	.fill 87
	.fill 111
	.fill 114
	.fill 108
	.fill 100
	.fill 33
	.fill 0
ZERO_CHAR:
	.fill 48

# Code Section:
print:
	# Function Prologue
	sw r7  r1  -1
	sw r2  r1  -2
	addi r1  r1  -2
	addi r2  r1  0
	# Function Body
	addi r1  r1  -8
	sw r3  r2  -8
	lw r3  r2  -8
	sw r3  r2  -1
print.for.0.start:
	movi r3 1
	sw r3  r2  -5
	lw r3  r2  -1
	lw r4  r3  0
	sw r4  r2  -7
	movi r3 0
	sw r3  r2  -6
	lw r3  r2  -7
	lw r4  r2  -6
	cmp r3  r4 
	bnz 1
	jmp 3
	movi r3 print.end.5
	jalr r0  r3 
	movi r3 0
	sw r3  r2  -5
print.end.5:
	lw r3  r2  -5
	movi r4 0
	cmp r3  r4 
	bz 1
	jmp 3
	movi r3 print.for.0.break
	jalr r0  r3 
	lw r3  r2  -1
	lw r4  r3  0
	sw r4  r2  -4
	lw r3  r2  -4
	call putchar
	sw r3  r2  -3
print.for.0.continue:
	lw r3  r2  -1
	sw r3  r2  -2
	lw r3  r2  -1
	movi r4 1
	add r3  r3  r4 
	sw r3  r2  -1
	movi r3 print.for.0.start
	jalr r0  r3 
print.for.0.break:
	movi r3 0
	# Function Epilogue
	mov r1  r2 
	lw r7  r2  1
	lw r2  r2  0
	addi r1  r1  2
	jalr r0  r7 
main:
	addi r1  r0  0
	addi r2  r0  0
	addi r1  r1  -2
	movi r3 hello
	sw r3  r2  -2
	lw r3  r2  -2
	call print
	sw r3  r2  -1
	movi r3 0
	# Function Epilogue
	sys EXIT
