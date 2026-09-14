#include "diagnostics.h"
#include <string.h>

static DtcCode detect(const BrakeCanInput *i, uint32_t now, uint32_t last, bool has, uint16_t command, const Diagnostics *d) {
    uint32_t index, sum = 0U, unchanged = 0U;
    (void)now;
    if (!has || now - last > BRAKE_CAN_TIMEOUT_MS) return DTC_CAN_TIMEOUT;
    if (!i->signal_valid) return DTC_MESSAGE_CORRUPT;
    if (i->brake_request_pct > 100U) return DTC_SIGNAL_INVALID;
    for (index = 0U; index < BRAKE_WHEEL_COUNT; ++index) {
        if (i->wheel_speed_kph[index] > 300U) return DTC_WHEEL_RANGE;
        sum += i->wheel_speed_kph[index];
        if (d->has_history && i->wheel_speed_kph[index] == d->last_wheels[index]) ++unchanged;
    }
    if (i->vehicle_speed_kph > 10U && sum / BRAKE_WHEEL_COUNT < i->vehicle_speed_kph / 2U) return DTC_WHEEL_MISMATCH;
    if (d->has_history && i->vehicle_speed_kph > 15U && unchanged == 1U) return DTC_WHEEL_STUCK;
    if (command > 2000U && i->pressure_feedback_kpa + 1500U < command) return DTC_PRESSURE_UNDER_RESPONSE;
    if (command == 0U && i->pressure_feedback_kpa > 1000U) return DTC_PRESSURE_STUCK_HIGH;
    if (command > 1000U && i->pressure_feedback_kpa < 100U) return DTC_PRESSURE_STUCK_LOW;
    return DTC_NONE;
}

void diagnostics_init(Diagnostics *d) { memset(d, 0, sizeof *d); }

void diagnostics_update(Diagnostics *d, const BrakeCanInput *i, uint32_t now, uint32_t last, bool has, uint16_t command) {
    DtcCode code = detect(i, now, last, has, command, d);
    if (code != DTC_NONE) {
        if (code != d->active) { d->active = code; d->since_ms = now; d->confirmed = false; }
        if (now - d->since_ms >= DIAG_CONFIRM_MS || code == DTC_CAN_TIMEOUT) d->confirmed = true;
        d->recovery_ms = 0U;
    } else if (d->active != DTC_NONE && !d->latched) {
        if (d->recovery_ms == 0U) d->recovery_ms = now;
        if (now - d->recovery_ms >= DIAG_RECOVERY_MS) { d->active = DTC_NONE; d->confirmed = false; }
    }
    if (has) { memcpy(d->last_wheels, i->wheel_speed_kph, sizeof d->last_wheels); d->has_history = true; }
    d->latched = d->active == DTC_CAN_TIMEOUT || d->active == DTC_PRESSURE_STUCK_HIGH;
    d->severity = d->confirmed ? ((d->active == DTC_WHEEL_STUCK || d->active == DTC_WHEEL_MISMATCH) ? DIAG_SEVERITY_DEGRADED : DIAG_SEVERITY_FAILSAFE) : DIAG_SEVERITY_NONE;
}

const char *diagnostics_dtc_name(DtcCode c) { static const char *names[] = {"NONE", "CAN_TIMEOUT", "WHEEL_RANGE", "WHEEL_STUCK", "WHEEL_MISMATCH", "PRESSURE_UNDER_RESPONSE", "PRESSURE_STUCK_HIGH", "PRESSURE_STUCK_LOW", "SIGNAL_INVALID", "MESSAGE_CORRUPT"}; return c <= DTC_MESSAGE_CORRUPT ? names[c] : "UNKNOWN"; }
