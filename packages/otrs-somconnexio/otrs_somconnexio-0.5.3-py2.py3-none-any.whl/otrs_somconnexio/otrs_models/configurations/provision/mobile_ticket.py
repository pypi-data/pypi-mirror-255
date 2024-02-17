# coding: utf-8
class MobileTicketConfiguration:
    process_id = "Process-325351399237c1e69144b17e471b1b51"
    activity_id = "Activity-90f09a366cd9426695ef0e21faeb4ed2"
    type = "Petición"
    queue_id = 71
    state = "new"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        if otrs_configuration:
            self.process_id = otrs_configuration.mobile_process_id
            self.activity_id = otrs_configuration.mobile_activity_id
            self.type = otrs_configuration.mobile_ticket_type
            self.queue_id = otrs_configuration.mobile_ticket_queue_id
            self.state = otrs_configuration.mobile_ticket_state
            self.priority = otrs_configuration.mobile_ticket_priority


class MobileTicketPausedConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-ad31188b18cac0d1af222360fce65757"
    queue_id = 197


class MobileTicketCompletedConfiguration(MobileTicketPausedConfiguration):
    # TODO review activity_id
    queue_id = 198


class MobileTicketRequestedConfiguration(MobileTicketConfiguration):
    # TODO review activity_id
    queue_id = 72
