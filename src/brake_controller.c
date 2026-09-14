#include "brake_controller.h"

uint16_t brake_controller_pressure(uint16_t request_pct, bool abs_active) {
    uint16_t bounded_request = request_pct > 100U ? 100U : request_pct;
    uint32_t pressure = ((uint32_t)bounded_request * BRAKE_MAX_PRESSURE_KPA) / 100U;
    if (abs_active) { pressure = (pressure * 70U) / 100U; }
    return (uint16_t)pressure;
}

bool brake_controller_abs_needed(const BrakeCanInput *input) {
    uint32_t i;
    if (input->vehicle_speed_kph < 10U || input->brake_request_pct < 10U) { return false; }
    for (i = 0U; i < BRAKE_WHEEL_COUNT; ++i) {
        if ((uint32_t)input->wheel_speed_kph[i] * 100U < (uint32_t)input->vehicle_speed_kph * 80U) { return true; }
    }
    return false;
}
