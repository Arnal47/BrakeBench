#if defined(_WIN32)
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "can_interface.h"
#include <stdio.h>

bool can_interface_decode_request(const char *line, BrakeCanInput *input) {
    unsigned int request, vehicle, w0, w1, w2, w3, timestamp;
    if (sscanf(line, "%u,%u,%u,%u,%u,%u,%u", &request, &vehicle, &w0, &w1, &w2, &w3, &timestamp) != 7) { return false; }
    if (request > 65535U || vehicle > 65535U || w0 > 65535U || w1 > 65535U || w2 > 65535U || w3 > 65535U) { return false; }
    input->brake_request_pct = (uint16_t)request; input->vehicle_speed_kph = (uint16_t)vehicle; input->wheel_speed_kph[0] = (uint16_t)w0; input->wheel_speed_kph[1] = (uint16_t)w1; input->wheel_speed_kph[2] = (uint16_t)w2; input->wheel_speed_kph[3] = (uint16_t)w3; input->received_at_ms = timestamp; return true;
}
void can_interface_encode_status(const BrakeCanOutput *output, char *buffer, uint32_t buffer_size) { (void)snprintf(buffer, buffer_size, "STATE=%s,ABS=%u,FAULT=%s,PRESSURE=%u", brake_ecu_state_name(output->state), output->abs_active ? 1U : 0U, brake_fault_name(output->fault), output->pressure_kpa); }
