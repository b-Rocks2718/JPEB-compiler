unsigned FRAME_BUFFER_TOP = 0xE000;
unsigned FRAME_BUFFER_SIZE = 0x2000;
unsigned SCREEN_WIDTH_TILES = 128;
unsigned SCREEN_HEIGHT_TILES = 64;

unsigned BLACK_BLACK = 0x0101;
unsigned BLACK_WHITE = 0x0100;
unsigned WHITE_BLACK = 0x0001;
unsigned WHITE_WHITE = 0x0000;

// unsigned IO_BUFFER = 

unsigned write_pair(unsigned color_pair, unsigned x, unsigned y) 
{
    // writes to the position (x,y) interpreted as singular tiles in
    // the frame

    // we don't have multiplication so we multiply by 80 like this
    // unsigned mem_index_y_portion = y << 4;
    // mem_index_y_portion = (mem_index_y_portion << 2) + mem_index_y_portion;

    unsigned mem_index = ((SCREEN_WIDTH_TILES * y) + x)/2;
    //(mem_index_y_portion + x) >> 1;

    *((unsigned*)(FRAME_BUFFER_TOP + mem_index)) = color_pair;
}

unsigned draw_square(unsigned x, unsigned y)
{
    // takes in two coordinates and draws a white square
    write_pair(BLACK_BLACK, x, y);
    write_pair(BLACK_BLACK, x, y + 1);
}

int main(void) {
    draw_square(0, 0);
}