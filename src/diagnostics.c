#include "diagnostics.h"

BrakeFaultCode diagnostics_validate(const BrakeCanInput *input, uint32_t now_ms, uint32_t last_can_ms, bool has_input) {
    uint32_t i;
    if (!has_input || (now_ms - last_can_ms) > BRAKE_CAN_TIMEOUT_MS) { return BRAKE_FAULT_CAN_TIMEOUT; }
    if (input->brake_request_pct > 100U) { return BRAKE_FAULT_PRESSURE; }
    if (input->vehicle_speed_kph > 300U) { return BRAKE_FAULT_WHEEL_SPEED; }
    for (i = 0U; i < BRAKE_WHEEL_COUNT; ++i) { if (input->wheel_speed_kph[i] > 300U) { return BRAKE_FAULT_WHEEL_SPEED; } }
    return BRAKE_FAULT_NONE;
}
