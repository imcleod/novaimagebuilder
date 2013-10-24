from time import sleep

class NovaInstance:

    def __init__(self, instance, stack_env):
        self.last_disk_activity = 0
        self.last_net_activity = 0
        self.instance = instance
        self.stack_env = stack_env
    
    @property
    def id(self):
        """


        @return:
        """
        return self.instance.id

    @property
    def status(self):
        """


        @return:
        """
        self.instance = self.stack_env.nova.servers.get(self.instance.id)
        return self.instance.status

    def get_disk_and_net_activity(self):
        """


        @return:
        """
        disk_activity = 0
        net_activity = 0
        diagnostics = self.instance.diagnostics()[1]
        if not diagnostics:
            return None, None
        for key, value in diagnostics.items():
            if ('read' in key) or ('write' in key):
                disk_activity += int(value)
            if ('rx' in key) or ('tx' in key):
                net_activity += int(value)
        return disk_activity, net_activity

    def is_active(self, inactivity_timeout):
        """

        @param inactivity_timeout:
        @return:
        """
        inactivity_countdown = inactivity_timeout
        while inactivity_countdown > 0: 
            self.log.debug("checking for inactivity")
            try:
                current_disk_activity, current_net_activity = self.get_disk_and_net_activity()
            except Exception, e:
                saved_exception = e
                break

            if (current_disk_activity == self.last_disk_activity) and \
                    (current_net_activity < (self.last_net_activity + 4096)):
                # if we saw no read or write requests since the last iteration,
                # decrement our activity timer
                inactivity_countdown -= 1
            else:
                # if we did see some activity, record it
                self.last_disk_activity = current_disk_activity
                self.last_net_activity = current_net_activity
                return True
    
            self.last_disk_activity = current_disk_activity
            self.last_net_activity = current_net_activity
            sleep(1)
        return False
