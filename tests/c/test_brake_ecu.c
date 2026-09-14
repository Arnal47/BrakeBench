#include "brake_ecu.h"
#include <assert.h>
#include <string.h>

static BrakeCanInput valid_input(uint16_t request, uint16_t speed, uint32_t time) {
    BrakeCanInput input;
    uint32_t i;
    memset(&input, 0, sizeof(input));
    input.brake_request_pct = request;
    input.vehicle_speed_kph = speed;
    input.received_at_ms = time;
    for (i = 0U; i < BRAKE_WHEEL_COUNT; ++i) { input.wheel_speed_kph[i] = speed; }
    return input;
}

int main(void) {
    BrakeEcu ecu;
    BrakeCanInput input = valid_input(50U, 80U, 100U);
    BrakeCanOutput output;
    brake_ecu_init(&ecu);
    brake_ecu_receive(&ecu, &input);
    brake_ecu_tick(&ecu, 100U);
    output = brake_ecu_output(&ecu);
    assert(output.state == BRAKE_ECU_BRAKING);
    assert(output.pressure_kpa == 6000U);

    input.wheel_speed_kph[2] = 50U;
    brake_ecu_receive(&ecu, &input);
    brake_ecu_tick(&ecu, 100U);
    output = brake_ecu_output(&ecu);
    assert(output.state == BRAKE_ECU_ABS_ACTIVE);
    assert(output.abs_active);
    assert(output.pressure_kpa == 4200U);

    brake_ecu_tick(&ecu, 201U);
    output = brake_ecu_output(&ecu);
    assert(output.state == BRAKE_ECU_FAULT);
    assert(output.fault == BRAKE_FAULT_CAN_TIMEOUT);

    input = valid_input(101U, 50U, 202U);
    brake_ecu_receive(&ecu, &input);
    brake_ecu_tick(&ecu, 202U);
    output = brake_ecu_output(&ecu);
    assert(output.fault == BRAKE_FAULT_PRESSURE);
    return 0;
}
