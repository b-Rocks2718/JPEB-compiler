	movi r3 main
	jalr r0  r3 

# Data Section:
WHITE_WHITE:
	.fill 0
WHITE_BLACK:
	.fill 1
BLACK_WHITE:
	.fill 256
BLACK_BLACK:
	.fill 257
SCREEN_HEIGHT_TILES:
	.fill 64
SCREEN_WIDTH_TILES:
	.fill 128
FRAME_BUFFER_SIZE:
	.fill 8192
FRAME_BUFFER_TOP:
	.fill 57344

# Code Section:
write_pair:
	# Function Prologue
	sw r7  r1  -1
	sw r2  r1  -2
	addi r1  r1  -2
	addi r2  r1  0
	# Function Body
	addi r1  r1  -10
	sw r3  r2  -1
	sw r4  r2  -2
	sw r5  r2  -3
	movi r3 SCREEN_WIDTH_TILES
	lw r3  r3  0
	lw r4  r2  -3
	call umul
	sw r3  r2  -4
	lw r3  r2  -4
	lw r4  r2  -2
	add r3  r3  r4 
	sw r3  r2  -5
	movi r3 2
	sw r3  r2  -6
	lw r3  r2  -5
	lw r4  r2  -6
	call udiv
	sw r3  r2  -7
	lw r3  r2  -7
	sw r3  r2  -8
	movi r3 FRAME_BUFFER_TOP
	lw r3  r3  0
	lw r4  r2  -8
	add r3  r3  r4 
	sw r3  r2  -9
	lw r3  r2  -9
	sw r3  r2  -10
	lw r3  r2  -10
	lw r4  r2  -1
	sw r4  r3  0
	movi r3 0
	# Function Epilogue
	mov r1  r2 
	lw r7  r2  1
	lw r2  r2  0
	addi r1  r1  2
	jalr r0  r7 
draw_square:
	# Function Prologue
	sw r7  r1  -1
	sw r2  r1  -2
	addi r1  r1  -2
	addi r2  r1  0
	# Function Body
	addi r1  r1  -6
	sw r3  r2  -1
	sw r4  r2  -2
	movi r3 BLACK_BLACK
	lw r3  r3  0
	lw r4  r2  -1
	lw r5  r2  -2
	call write_pair
	sw r3  r2  -3
	movi r3 1
	sw r3  r2  -4
	lw r3  r2  -2
	lw r4  r2  -4
	add r3  r3  r4 
	sw r3  r2  -5
	movi r3 BLACK_BLACK
	lw r3  r3  0
	lw r4  r2  -1
	lw r5  r2  -5
	call write_pair
	sw r3  r2  -6
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
	addi r1  r1  -3
	movi r3 0
	sw r3  r2  -1
	movi r3 0
	sw r3  r2  -2
	lw r3  r2  -1
	lw r4  r2  -2
	call draw_square
	sw r3  r2  -3
	movi r3 0
	# Function Epilogue
	sys EXIT
