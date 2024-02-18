"""
SCAN PLUGINS

All new scans should be derived from ScanBase. ScanBase provides various methods that can be customized and overriden
but they are executed in a specific order:

- self.initialize                        # initialize the class if needed
- self.read_scan_motors                  # used to retrieve the start position (and the relative position shift if needed)
- self.prepare_positions                 # prepare the positions for the scan. The preparation is split into multiple sub fuctions:
    - self._calculate_positions          # calculate the positions
    - self._set_positions_offset         # apply the previously retrieved scan position shift (if needed)
    - self._check_limits                 # tests to ensure the limits won't be reached
- self.open_scan                         # send an open_scan message including the scan name, the number of points and the scan motor names
- self.stage                             # stage all devices for the upcoming acquisiton
- self.run_baseline_readings             # read all devices to get a baseline for the upcoming scan
- self.scan_core                         # run a loop over all position
    - self._at_each_point(ind, pos)      # called at each position with the current index and the target positions as arguments
- self.finalize                          # clean up the scan, e.g. move back to the start position; wait everything to finish
- self.unstage                           # unstage all devices that have been staged before
- self.cleanup                           # send a close scan message and perform additional cleanups if needed
"""

import time

from bec_lib import messages, MessageEndpoints, bec_logger

from scan_server.scans import FlyScanBase, ScanAbortion

logger = bec_logger.logger


class OwisGrid(FlyScanBase):
    """Owis-based grid scan."""

    scan_name = "owis_grid"
    scan_report_hint = "scan_progress"
    required_kwargs = []
    arg_input = {}
    arg_bundle_size = {"bundle": len(arg_input), "min": None, "max": None}
    enforce_sync = False

    def __init__(
        self,
        start_y: float,
        end_y: float,
        interval_y: int,
        start_x: float,
        end_x: float,
        interval_x: int,
        *args,
        exp_time: float = 0.1,
        readout_time: float = 3e-3,
        **kwargs,
    ):
        """
        Owis-based grid scan.

        Args:
            start_y (float): start position of y axis (fast axis)
            end_y (float): end position of y axis (fast axis)
            interval_y (int): number of points in y axis
            start_x (float): start position of x axis (slow axis)
            end_x (float): end position of x axis (slow axis)
            interval_x (int): number of points in x axis
            exp_time (float): exposure time in seconds. Default is 0.1s
            readout_time (float): readout time in seconds, minimum of 3e-3s (3ms)

        Exp:
           scans.sgalil_grid(start_y = val1, end_y= val1, interval_y = val1, start_x = val1, end_x = val1, interval_x = val1, exp_time = 0.02, readout_time = 3e-3)


        """
        super().__init__(*args, **kwargs)

        # Enforce scanning from positive to negative
        if start_y > end_y:
            self.start_y = start_y
            self.end_y = end_y
        else:
            self.start_y = end_y
            self.end_y = start_y
        if start_x > end_x:
            self.start_x = start_x
            self.end_x = end_x
        else:
            self.start_x = end_x
            self.end_x = start_x
        # set scan parameter
        self.interval_y = interval_y
        self.interval_x = interval_x
        self.exp_time = exp_time
        self.readout_time = readout_time
        self.num_pos = int(interval_x * interval_y)
        self.scan_motors = ["samx", "samy"]

        # Scan progress related variables
        self.timeout_progress = 0
        self.progress_point = 0
        self.timeout_scan_abortion = 10  # 42 # duty cycles of scan segment update
        self.sleep_time = 1

        # Keep the shutter open for longer to allow acquisitions to fly in
        self.shutter_additional_width = 0.15

        # Scan related variables
        self.sign = 1
        # add offset time if needed
        self.add_pre_move_time = 0.0

        self.stepping_x = None
        self.stepping_y = None
        self.high_velocity = None
        self.high_acc_time = None
        self.base_velocity = None
        self.target_velocity = None
        self.acc_time = None
        self.premove_distance = None

    def get_initial_motor_properties(self):
        self.high_velocity = yield from self.stubs.send_rpc_and_wait("samy", "velocity.get")
        self.high_acc_time = yield from self.stubs.send_rpc_and_wait("samy", "acceleration.get")
        self.base_velocity = yield from self.stubs.send_rpc_and_wait("samy", "base_velocity.get")

    def compute_scan_params(self):
        """Compute scan parameters. This includes the velocity, acceleration and premove distance."""

        ########### Owis stage parameters
        # scanning related parameters
        self.stepping_y = abs(self.start_y - self.end_y) / self.interval_y
        self.stepping_x = abs(self.start_x - self.end_x) / self.interval_x

        # Get current velocity, acceleration and base_velocity
        yield from self.get_initial_motor_properties()

        # Relevant parameters for scan
        self.target_velocity = self.stepping_y / (self.exp_time + self.readout_time)
        self.acc_time = (
            (self.target_velocity - self.base_velocity)
            / (self.high_velocity - self.base_velocity)
            * self.high_acc_time
        )
        self.premove_distance = (
            0.5 * (self.target_velocity + self.base_velocity) * self.acc_time
            + self.add_pre_move_time * self.target_velocity
        )

        # Checks and set acc_time and premove for the designated scan
        if self.target_velocity > self.high_velocity or self.target_velocity < self.base_velocity:
            raise ScanAbortion(
                f"Requested velocity of {self.target_velocity} exceeds {self.high_velocity}"
            )

    def scan_report_instructions(self):
        """Scan report instructions for the progress bar, yields from mcs card"""
        if not self.scan_report_hint:
            yield None
            return
        yield from self.stubs.scan_report_instruction({"scan_progress": ["mcs"]})

    def pre_scan(self):
        """Pre scan instructions, move to start position"""
        yield from self._move_and_wait([self.start_x, self.start_y])
        yield from self.stubs.pre_scan()

    def scan_progress(self) -> int:
        """Timeout of the progress bar. This gets updated in the frequency of scan segments"""
        raw_msg = self.device_manager.producer.get(MessageEndpoints.device_progress("mcs"))
        if not raw_msg:
            self.timeout_progress += 1
            return self.timeout_progress
        msg = messages.ProgressMessage.loads(raw_msg)
        if not msg:
            self.timeout_progress += 1
            return self.timeout_progress
        updated_progress = int(msg.content["value"])
        if updated_progress == int(self.progress_point):
            self.timeout_progress += 1
            return self.timeout_progress
        else:
            self.timeout_progress = 0
            self.progress_point = updated_progress
            return self.timeout_progress

    def scan_core(self):
        """This is the main event loop."""

        # Compute scan parameters including velocity, acceleration and premove distance
        yield from self.compute_scan_params()

        # Start acquisition with 10ms delay to allow fast shutter to open
        yield from self.stubs.send_rpc_and_wait(
            "ddg_detectors",
            "burst_enable",
            count=self.interval_y,
            delay=0.01,
            period=(self.exp_time + self.readout_time),
            config="first",
        )
        yield from self.stubs.send_rpc_and_wait(
            "ddg_mcs",
            "burst_enable",
            count=self.interval_y,
            delay=0,
            period=(self.exp_time + self.readout_time),
            config="first",
        )

        yield from self.stubs.send_rpc_and_wait("ddg_fsh", "burst_disable")

        # Set width of signals from ddg fsh to 0, except the one to the MCS card
        yield from self.stubs.send_rpc_and_wait(
            "ddg_fsh",
            "set_channels",
            "width",
            0,
            channels=["channelCD"],
        )
        yield from self.stubs.send_rpc_and_wait(
            "ddg_fsh",
            "set_channels",
            "width",
            0,
            channels=["channelEF", "channelGH"],
        )
        # Trigger MCS card to enable the acquisition
        time.sleep(0.05)
        yield from self.stubs.send_rpc_and_wait("ddg_fsh", "trigger")
        time.sleep(0.05)

        # Set width of signal to fast shutter to appropriate value for single lines
        yield from self.stubs.send_rpc_and_wait(
            "ddg_fsh",
            "set_channels",
            "width",
            (self.interval_y * (self.exp_time + self.readout_time) + self.shutter_additional_width),
            channels=["channelCD"],
        )

        # Set width of signal to MCS card to 0 --> It is already enabled
        yield from self.stubs.send_rpc_and_wait(
            "ddg_fsh",
            "set_channels",
            "width",
            0,
            channels=["channelAB"],
        )

        # remove delay for signals of ddg_mcs
        yield from self.stubs.send_rpc_and_wait("ddg_mcs", "set_channels", "delay", 0)

        # Set ddg_mcs on ext trigger from ddg_detectors
        status_ddg_mcs_source = yield from self.stubs.send_rpc_and_wait("ddg_mcs", "source.set", 1)
        # Set ddg_detectors and ddg_fsh to software trigger
        status_ddg_detectors_source = yield from self.stubs.send_rpc_and_wait(
            "ddg_detectors", "source.set", 5
        )
        # Set ddg_fsh to software trigger
        status_ddg_fsh_source = yield from self.stubs.send_rpc_and_wait("ddg_fsh", "source.set", 5)

        # Wait for a signal from all ddgs, this ensures that all commands before were executed
        status_ddg_mcs_source.wait()
        status_ddg_detectors_source.wait()
        status_ddg_fsh_source.wait()

        # Prepare motors
        # Move to start position (taking premove_distance for acceleration into account)
        status_prepos = yield from self.stubs.send_rpc_and_wait(
            "samy", "move", (self.start_y - self.premove_distance)
        )
        status_prepos.wait()

        # Set speed and acceleration for scan
        yield from self.stubs.send_rpc_and_wait("samy", "velocity.put", self.target_velocity)
        yield from self.stubs.send_rpc_and_wait("samy", "acceleration.put", self.acc_time)

        for ii in range(self.interval_x):
            # Set speed and acceleration
            yield from self.stubs.send_rpc_and_wait("samy", "velocity.put", self.target_velocity)
            yield from self.stubs.send_rpc_and_wait("samy", "acceleration.put", self.acc_time)

            # Start motion and send triggers
            yield from self.stubs.set(
                device="samy",
                value=(self.end_y + (self.sign * self.premove_distance)),
                wait_group="flyer",
            )
            # Trigger fast shutter, open them right away
            yield from self.stubs.send_rpc_and_wait("ddg_fsh", "trigger")

            time.sleep(self.acc_time)

            # Trigger detectors
            yield from self.stubs.send_rpc_and_wait("ddg_detectors", "trigger")

            # Readout primary devices, this waits and could lead to additional overheads
            # if devices are slow to response. For optimizing performance, primary devices
            # could be read out only once at beginning and end
            yield from self.stubs.read_and_wait(
                group="primary", wait_group="readout_primary", pointID=self.pointID
            )
            self.pointID += 1

            # Wait for motion to finish
            yield from self.stubs.wait(device="samy", wait_group="flyer", wait_type="move")

            # Move second axis by a step
            yield from self.stubs.set(
                device="samx", value=(self.start_x - ii * self.stepping_x), wait_group="motion"
            )
            # Set acceleration and velocity to max
            yield from self.stubs.send_rpc_and_wait("samy", "velocity.put", self.high_velocity)
            yield from self.stubs.send_rpc_and_wait("samy", "acceleration.put", self.high_acc_time)

            # Move back to start
            status_prepos = yield from self.stubs.send_rpc_and_wait(
                "samy", "move", (self.start_y - self.premove_distance)
            )

            # Wait for motion to finish
            status_prepos.wait()

    # Set speed and acceleration to initial values
    def finalize(self):
        """Finalize scan, set motor speed and acceleration to initial values"""
        yield from self.stubs.send_rpc_and_wait("samy", "velocity.put", self.high_velocity)
        yield from self.stubs.send_rpc_and_wait("samy", "acceleration.put", self.high_acc_time)
        super().finalize()
