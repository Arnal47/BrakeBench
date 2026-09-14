#include "can_application_adapter.h"

void can_application_deliver(BrakeEcu *ecu, const BrakeCanInput *decoded, uint32_t now_ms) {
    brake_ecu_receive(ecu, decoded);
    brake_ecu_tick(ecu, now_ms);
}

void can_application_deliver_invalid(BrakeEcu *ecu, uint32_t now_ms) {
    BrakeCanInput invalid = {0};
    invalid.signal_valid = false;
    invalid.received_at_ms = now_ms;
    can_application_deliver(ecu, &invalid, now_ms);
}
