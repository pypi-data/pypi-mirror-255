from dataclasses import dataclass
from pathlib import Path

from morbin import Morbin, Output


@dataclass
class Server:
    name: str
    country: str
    protocol: str
    load: str
    plan: str
    features: str | None


@dataclass(init=False)
class KillSwitch:
    active: bool
    on: bool
    permanent: bool

    def __init__(self, status: str):
        if status == "Off":
            self.on = False
            self.active = False
            self.permanent = False
        elif status.startswith("On (Inactive,"):
            self.on = True
            self.active = False
            self.permanent = False
        elif status == "On":
            self.on = True
            self.active = True
            self.permanent = False
        elif status == "Permanent":
            self.on = True
            self.active = True
            self.permanent = True


@dataclass(init=False)
class Connection:
    IP: str
    killswitch: KillSwitch
    raw: str
    server: Server
    time: str

    def __init__(self, status: str):
        self.raw = status
        lines = [line for line in status.splitlines() if ":" in line]
        connection = {
            line.split(":", 1)[0]: line.split(":", 1)[1].replace("\t", "").strip()
            for line in lines
        }
        self.IP = connection["IP"]
        self.server = Server(
            connection["Server"],
            connection["Country"],
            connection["Protocol"],
            connection["Server Load"],
            connection["Server Plan"],
            connection.get("Server Features"),
        )
        self.killswitch = KillSwitch(connection["Kill switch"])
        self.time = connection["Connection time"]

    def __str__(self) -> str:
        return self.raw


class Proton(Morbin):
    @property
    def program(self) -> str:
        return "protonvpn-cli"

    # Seat |=============================== Core ===============================|

    def config(self, args: str = "") -> Output:
        return self.run(f"config {args}")

    def connect(
        self,
        server: str = "",
        protocol: str = "",
        country_code: str = "",
        fastest: bool = False,
        random: bool = False,
        secure_core: bool = False,
        p2p: bool = False,
        tor: bool = False,
    ) -> Output:
        """
        #### :params:

        `server`: Connect to this specific server (e.g. `CH#4`, `CH-US-1`, `HK5-Tor`).

        `protocol`: Connect using this protocol (`tcp` or `udp`).

        `country_code`: Connect to a server in this country (`SE`, `PT`, `BR`, `AR`, etc.).

        `fastest`: Connect to the fastest server.

        `random`: Connect to a random server.

        `secure_core`: Connect to the fastest Secure-Core server.

        `p2p`: Connect to the fastest P2P server.

        `tor`: Connect to the fastest Tor server.

        Supplying an argument for `server` will override other parameters except `protocol`.

        If supplying one of the `bool` params (`fastest`, `random`, `secure_core`, `p2p`, `tor`), supply only one.
        They will be checked in the order they appear in the function signature and the first that is `True` will be used.
        """
        args = ""
        if server:
            args = server
        elif fastest:
            args = "--fastest"
        elif random:
            args = "--random"
        elif secure_core:
            args = "--sc"
        elif p2p:
            args = "--p2p"
        elif tor:
            args = "--tor"
        if country_code and (not server):
            args += f" --cc {country_code}"
        if protocol:
            args += f" --protocol {protocol}"
        return self.run(f"connect {args}")

    def disconnect(self) -> Output:
        return self.run("disconnect")

    def killswitch(self, arg: str) -> Output:
        """`arg` should be one of `on`, `off`, or `permanent`."""
        return self.run(f"killswitch --{arg}")

    def login(self, username: str) -> Output:
        return self.run(f"login {username}")

    def logout(self) -> Output:
        return self.run("logout")

    def netshield(self, args: str = "") -> Output:
        return self.run(f"netshield {args}")

    def reconnect(self) -> Output:
        return self.run("reconnect")

    def status(self) -> Output:
        """Execute status command."""
        return self.run("status")

    # Seat |=========================== Convenience ===========================|

    @property
    def connected(self) -> bool:
        """Returns whether this device is connected to Proton."""
        with self.capturing_output():
            status = self.status().stdout
        return "Proton VPN Connection Status" in status

    @property
    def connection(self) -> Connection | None:
        """If this device is connected, a `Connection` object will be returned.
        If disconnected, `None` will be returned.

        Accessing this property can be time consuming due to the protonvpn-cli backend.
        Ideally store it in a local variable until you need to check for an updated connection status.
        """
        with self.capturing_output():
            if self.connected:
                return Connection(self.status().stdout)
            return None

    def clear_cache(self):
        """Clears files from `home/.cache/protonvpn`.

        This seems to help with the time taken to connect sometimes,
        but if the permanent kill switch is engaged and you try to connect after clearing the cache, you will get an error.
        """
        path = Path.home() / ".cache" / "protonvpn"
        if path.exists():
            [path.unlink() for path in path.glob("*.*")]

    def connect_fastest(self) -> Output:
        """Connect to the fastest server."""
        return self.connect(fastest=True)

    def connect_random(self) -> Output:
        """Connect to a random server."""
        return self.connect(random=True)

    def disable_killswitch(self) -> Output:
        return self.killswitch("off")

    def enable_killswitch(self) -> Output:
        return self.killswitch("on")

    def enable_permanent_killswitch(self) -> Output:
        return self.killswitch("permanent")
