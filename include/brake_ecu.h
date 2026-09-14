#ifndef BRAKE_ECU_H
#define BRAKE_ECU_H

#include <stdbool.h>
#include <stdint.h>

#define BRAKE_WHEEL_COUNT 4U
#define BRAKE_CAN_TIMEOUT_MS 100U
#define BRAKE_MAX_PRESSURE_KPA 12000U

typedef enum { BRAKE_ECU_INIT, BRAKE_ECU_IDLE, BRAKE_ECU_BRAKING, BRAKE_ECU_ABS_ACTIVE, BRAKE_ECU_FAULT } BrakeEcuState;
typedef enum { BRAKE_FAULT_NONE = 0, BRAKE_FAULT_CAN_TIMEOUT = 1, BRAKE_FAULT_WHEEL_SPEED = 2, BRAKE_FAULT_PRESSURE = 3 } BrakeFaultCode;
typedef enum { DTC_NONE, DTC_CAN_TIMEOUT, DTC_WHEEL_RANGE, DTC_WHEEL_STUCK, DTC_WHEEL_MISMATCH, DTC_PRESSURE_UNDER_RESPONSE, DTC_PRESSURE_STUCK_HIGH, DTC_PRESSURE_STUCK_LOW, DTC_SIGNAL_INVALID, DTC_MESSAGE_CORRUPT } DtcCode;
typedef enum { DIAG_SEVERITY_NONE, DIAG_SEVERITY_DEGRADED, DIAG_SEVERITY_FAILSAFE } DiagnosticSeverity;

typedef struct { uint16_t brake_request_pct; uint16_t vehicle_speed_kph; uint16_t wheel_speed_kph[BRAKE_WHEEL_COUNT]; uint16_t pressure_feedback_kpa; bool signal_valid; uint32_t received_at_ms; } BrakeCanInput;
typedef struct { BrakeEcuState state; BrakeFaultCode fault; uint16_t pressure_kpa; bool abs_active; DtcCode dtc; DiagnosticSeverity severity; bool failsafe; } BrakeCanOutput;
typedef struct BrakeEcu BrakeEcu;


void brake_ecu_init(BrakeEcu *ecu);
void brake_ecu_receive(BrakeEcu *ecu, const BrakeCanInput *input);
void brake_ecu_tick(BrakeEcu *ecu, uint32_t now_ms);
void brake_ecu_clear_latched_dtc(BrakeEcu *ecu);
BrakeCanOutput brake_ecu_output(const BrakeEcu *ecu);
const char *brake_ecu_state_name(BrakeEcuState state);
const char *brake_fault_name(BrakeFaultCode fault);

typedef struct { DtcCode active; DiagnosticSeverity severity; uint32_t since_ms; uint32_t recovery_ms; uint16_t last_wheels[BRAKE_WHEEL_COUNT]; bool confirmed; bool latched; bool has_history; } Diagnostics;
struct BrakeEcu { BrakeCanInput input; BrakeCanOutput output; uint32_t last_can_ms; bool has_input; Diagnostics diagnostics; };
#endif
