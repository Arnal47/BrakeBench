#ifndef CAN_APPLICATION_ADAPTER_H
#define CAN_APPLICATION_ADAPTER_H

#include "brake_ecu.h"

/* Transport-independent boundary: a DBC decoder supplies already-scaled signals. */
void can_application_deliver(BrakeEcu *ecu, const BrakeCanInput *decoded, uint32_t now_ms);
void can_application_deliver_invalid(BrakeEcu *ecu, uint32_t now_ms);

#endif
