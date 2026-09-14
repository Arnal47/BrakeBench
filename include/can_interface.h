#ifndef CAN_INTERFACE_H
#define CAN_INTERFACE_H
#include "brake_ecu.h"
bool can_interface_decode_request(const char *line, BrakeCanInput *input);
void can_interface_encode_status(const BrakeCanOutput *output, char *buffer, uint32_t buffer_size);
#endif
