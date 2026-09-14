#include "brake_ecu.h"
#include "brake_controller.h"
#include "diagnostics.h"

void brake_ecu_init(BrakeEcu *ecu) {
    ecu->output.state = BRAKE_ECU_INIT; ecu->output.fault = BRAKE_FAULT_NONE; ecu->output.pressure_kpa = 0U; ecu->output.abs_active = false;
    ecu->last_can_ms = 0U; ecu->has_input = false;
}
void brake_ecu_receive(BrakeEcu *ecu, const BrakeCanInput *input) { ecu->input = *input; ecu->last_can_ms = input->received_at_ms; ecu->has_input = true; }
void brake_ecu_tick(BrakeEcu *ecu, uint32_t now_ms) {
    BrakeFaultCode fault = diagnostics_validate(&ecu->input, now_ms, ecu->last_can_ms, ecu->has_input);
    bool abs_needed;
    if (fault != BRAKE_FAULT_NONE) { ecu->output.state = BRAKE_ECU_FAULT; ecu->output.fault = fault; ecu->output.pressure_kpa = 0U; ecu->output.abs_active = false; return; }
    ecu->output.fault = BRAKE_FAULT_NONE;
    if (ecu->input.brake_request_pct == 0U) { ecu->output.state = BRAKE_ECU_IDLE; ecu->output.pressure_kpa = 0U; ecu->output.abs_active = false; return; }
    abs_needed = brake_controller_abs_needed(&ecu->input); ecu->output.abs_active = abs_needed;
    ecu->output.state = abs_needed ? BRAKE_ECU_ABS_ACTIVE : BRAKE_ECU_BRAKING;
    ecu->output.pressure_kpa = brake_controller_pressure(ecu->input.brake_request_pct, abs_needed);
}
BrakeCanOutput brake_ecu_output(const BrakeEcu *ecu) { return ecu->output; }
const char *brake_ecu_state_name(BrakeEcuState state) { static const char *names[] = {"INIT", "IDLE", "BRAKING", "ABS_ACTIVE", "FAULT"}; return state <= BRAKE_ECU_FAULT ? names[state] : "UNKNOWN"; }
const char *brake_fault_name(BrakeFaultCode fault) { static const char *names[] = {"NONE", "CAN_TIMEOUT", "WHEEL_SPEED", "PRESSURE"}; return fault <= BRAKE_FAULT_PRESSURE ? names[fault] : "UNKNOWN"; }
