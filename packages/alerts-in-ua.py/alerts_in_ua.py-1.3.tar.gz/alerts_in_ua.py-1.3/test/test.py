import asyncio
from time import time, sleep

from pprint import pprint
from alerts_in_ua.alerts_client import AlertsClient
from alerts_in_ua.async_alerts_client import AsyncAlertsClient
from alerts_in_ua.locations import Locations
from alerts_in_ua.exceptions import NotAuthorized

alerts_client = AsyncAlertsClient("04fb0e20d084953e768100bbcfec463b81b1191aab2203")


async def main():
    locations = await alerts_client.get_active()
    air_raid_locations = locations.filter(alert_type="air_raid")
    print(air_raid_locations)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
