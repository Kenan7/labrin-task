from user_agents import parse


class InformationParser:
    def __init__(self, ua_string):
        self.user_agent = ua_string

    def get_device(self):
        user_agent = parse(self.user_agent)
        device_obj = user_agent.device  # Create a device object
        family = device_obj.family  # Equipment name
        brand = device_obj.brand  # Equipment vendor
        model = device_obj.model  # Equipment type
        data = {
            "family": family,
            "brand": brand,
            "model": model,
        }

        return data

    def get_browser(self):
        user_agent = parse(self.user_agent)
        browser_obj = user_agent.browser  # Create a browser object
        family = browser_obj.family  # Browser type
        version = browser_obj.version  # version number
        data = {
            "family": family,
            "version": version,
        }

        return data

    def get_os(self):
        user_agent = parse(self.user_agent)
        os_obj = user_agent.os  # Create an operating system object
        family = os_obj.family  # System name
        version = os_obj.version  # System version number
        data = {
            "family": family,
            "version": version,
        }

        return data
