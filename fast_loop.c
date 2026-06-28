






#include <stdint.h>

/*
uint64_t means unsigned 64-bit integer.
We use it because the total can become large.

Python will call this function once.
Then C does all the looping internally.

*/
uint64_t sum_squares_c(uint64_t n){

    uint64_t total = 0;

    for(uint64_t i = 0; i < n; i++){
        total += i*i;
    }
    return total;

}