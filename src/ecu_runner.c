#if defined(_WIN32)
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "brake_ecu.h"
#include "can_interface.h"
#include <stdio.h>

int main(void) {
    BrakeEcu ecu;
    char line[128];
    char status[128];
    BrakeCanInput input;

    brake_ecu_init(&ecu);
    while (fgets(line, sizeof line, stdin) != NULL) {
        BrakeCanOutput output;
        if (can_interface_decode_request(line, &input)) {
            brake_ecu_receive(&ecu, &input);
            brake_ecu_tick(&ecu, input.received_at_ms);
        } else {
            unsigned long now;
            if (sscanf(line, "TICK,%lu", &now) == 1) {
                brake_ecu_tick(&ecu, (uint32_t)now);
            }
        }
        output = brake_ecu_output(&ecu);
        can_interface_encode_status(&output, status, sizeof status);
        puts(status);
        fflush(stdout);
    }
    return 0;
}
