import logging
import re

from aprsd import packets, plugin, plugin_utils
from aprsd.utils import trace
from oslo_config import cfg

import aprsd_locationdata_plugin
from aprsd_locationdata_plugin import conf  # noqa


CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class LocationDataPlugin(plugin.APRSDRegexCommandPluginBase, plugin.APRSFIKEYMixin):

    version = aprsd_locationdata_plugin.__version__
    # Change this regex to match for your plugin's command
    # Tutorial on regex here: https://regexone.com/
    # Look for any command that starts with w or W
    command_regex = r"^([ld]|[ld]\s)"
    command_name = "location data"
    # the command is for ?
    # Change this value to a 1 word description of the plugin
    # this string is used for help
    short_description = "Where in the world is a CALLSIGN's last GPS beacon?"
    enabled = False

    def setup(self):
        self.ensure_aprs_fi_key()

    def create_threads(self):
        """This allows you to create and return a custom APRSDThread object.

        Create a child of the aprsd.threads.APRSDThread object and return it
        It will automatically get started.

        You can see an example of one here:
        https://github.com/craigerl/aprsd/blob/master/aprsd/threads.py#L141
        """
        if self.enabled:
            # You can create a background APRSDThread object here
            # Just return it for example:
            # https://github.com/hemna/aprsd-weewx-plugin/blob/master/aprsd_weewx_plugin/aprsd_weewx_plugin.py#L42-L50
            #
            return []

    @trace.trace
    def process(self, packet: packets.core.Packet):

        """This is called when a received packet matches self.command_regex.

        This is only called when self.enabled = True and the command_regex
        matches in the contents of the packet["message_text"]."""

        LOG.info("LocationDataPlugin Plugin")
        fromcall = packet.from_call
        message = packet.get("message_text", None)

        api_key = CONF.aprs_fi.apiKey

        # optional second argument is a callsign to search
        a = re.search(r"^.*\s+(.*)", message)
        if a is not None:
            searchcall = a.group(1)
            searchcall = searchcall.upper()
        else:
            # if no second argument, search for calling station
            searchcall = fromcall

        try:
            aprs_data = plugin_utils.get_aprs_fi(api_key, searchcall)
        except Exception as ex:
            LOG.error(f"Failed to fetch aprs.fi '{ex}'")
            return "Failed to fetch aprs.fi location"

        LOG.debug(f"LocationPlugin: aprs_data = {aprs_data}")
        if not len(aprs_data["entries"]):
            LOG.error("Didn't get any entries from aprs.fi")
            return f"{searchcall}:None"

        lat = float(aprs_data["entries"][0]["lat"])
        lon = float(aprs_data["entries"][0]["lng"])

        try:  # altitude not always provided
            alt = float(aprs_data["entries"][0]["altitude"])
        except Exception:
            alt = 0
        # int(alt * 3.28084)
        course = aprs_data["entries"][0].get("course", 0)
        speed = aprs_data["entries"][0].get("speed", 0)
        aprs_lasttime_seconds = aprs_data["entries"][0]["lasttime"]

        # Format is
        # callsign:latitude,longitude,altitude,course,speed,timestamp
        reply = "^ld^{}:{},{},{},{},{},{}".format(
            searchcall,
            f"{lat:0.5f}",
            f"{lon:0.5f}",
            f"{float(alt):0.0f}",
            f"{float(course):0.0f}",
            f"{float(speed):0.1f}",
            aprs_lasttime_seconds,
        ).rstrip()

        return reply
