import nio.events.room_events
import nio.events.to_device
from nio import InviteMemberEvent

from .utils import info, error

class Callbacks:
    """
    A class for handling callbacks.
    """

    def __init__(self, async_client, bot) -> None:
        self.async_client = async_client
        self.bot = bot

    async def setup(self) -> None:
        """
        Add callbacks to async_client
        """
        self.async_client.add_event_callback(self.invite_callback,
                                                 InviteMemberEvent)

        for event_listener in self.bot.listener._registry:
            if issubclass(event_listener[1],
                          nio.events.to_device.ToDeviceEvent):
                self.async_client.add_to_device_callback(
                    event_listener[0], event_listener[1])
            else:
                self.async_client.add_event_callback(event_listener[0],
                                                     event_listener[1])

    async def invite_callback(self, room, event, tries=1) -> None:
        """
        Callback for handling invites.

        Parameters
        ----------
        room : nio.rooms.MatrixRoom
        event : nio.events.room_events.InviteMemberEvent
        tries : int, optional
            Amount of times that this function has been called in a row for the same exact event.

        """
        if not event.membership == "invite":
            return

        try:
            await self.async_client.join(room.room_id)
            info(f"Joined {room.room_id}")
        except Exception as e:
            error(f"Error joining {room.room_id}: {e}")
            tries += 1
            if not tries == 3:
                info("Trying again...")
                await self.invite_callback(room, event, tries)
            else:
                error(f"Failed to join {room.room_id} after 3 tries")


