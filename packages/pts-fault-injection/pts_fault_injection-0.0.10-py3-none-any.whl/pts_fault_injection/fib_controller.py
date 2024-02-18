import os
import can
import sys
import time
import logging
import cantools
from typing import List
from cantools.database.can.signal import NamedSignalValue

broadcast_id = 0x600
board_ids = {0: "Standard Signals 1",
             1: "Standard Signals 2",
             2: "Standard Signals 3",
             3: "Standard Signals 4",
             4: "Analog Signals",
             5: "Bus Signals",
             6: "HV Signals",
             9: "Contactor Card",
             10: "HV Box Card",
             14: "DAC Board",
             15: "Break Out Box",
             16: "CMB Faults"
             }

dac_setpoints = [-1, -1, -1, -1, -1, -1, -1, -1]  # 8 DAC Channels
dac_mapping = {0: 9,
               1: 1,
               2: 5,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7}  # DAC Channel : Message Channel


def test_card(card):
    funcs = {
        "AnalogSignal": AnalogSignalCard.test_analog_signal_card,
        "StandardSignal1": StandardSignalCard.test_standard_signal_card1,
        "StandardSignal2": StandardSignalCard.test_standard_signal_card2,
        "StandardSignal3": StandardSignalCard.test_standard_signal_card3,
        "StandardSignal4": StandardSignalCard.test_standard_signal_card4,
        "BusSignal": BusSignalCard.test_bus_signal_card,
        "HVSignal": HVSignalCard.test_hv_signal_card,
    }
    if card in funcs:
        print(f"TESTING BOARD {card}")
        funcs[card]()
    else:
        raise Exception(f"Signal Card {card} not present.")


class FaultInjectionController(object):
    """
    Base class for the Fault Injection Box Controller
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, dbc_dir=os.path.join(os.path.dirname(__file__))+"/dbc/"):
        self.can_db = cantools.database.Database()
        self.bus = None
        self.dbc_dir = dbc_dir
        self.card_state = 0
        logging.info(f"Searching for DBCs in {self.dbc_dir}")
        for file in os.listdir(self.dbc_dir):
            if file.endswith(".dbc"):
                logging.info(f"adding {file}")
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), self.dbc_dir + file))
        self.signal_cards = [
            StandardSignalCard(),
            StandardSignalCard(),
            StandardSignalCard(),
            StandardSignalCard(),
            AnalogSignalCard(),
            BusSignalCard(),
            HVSignalCard(),
        ]
        return

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def read_FW_Response(self):
        time.sleep(1)
        wait_time = 1 + time.time()
        msg = self.bus.recv(timeout=1)
        rdy_IDs = []
        msg_buf = {}
        fw_versions = {}
        print("Searching for ready controllers.")
        while wait_time > time.time():
            if msg is not None and msg.dlc > 0:
                if 0x6FF > msg.arbitration_id > 0x600:
                    rdy_IDs.append(msg.arbitration_id)
                    msg_buf[msg.arbitration_id] = msg.data
                sys.stdout.write(".")
                sys.stdout.flush()
            msg = self.bus.recv(timeout=0.1)
        try:
            for id in rdy_IDs:
                fw_versions[id] = msg_buf[id].decode("ASCII")
        except Exception as e:
            raise Exception(f"\nError in finding FW versions for all responses {e}")
        return rdy_IDs, fw_versions

    def read_FW_Versions(self):
        # Writing FW Update Request
        logging.info("Using broadcast ID " + hex(broadcast_id))
        msg = can.Message(arbitration_id=broadcast_id, data=[ord('F'), ord('W'), ord('?'), 0, 0, 0, 0, 0],
                          is_extended_id=False)
        self.bus.send(msg)
        # Block until ready
        ids, fw_versions = self.read_FW_Response()
        for id in ids:
            try:
                logging.info("\nFW Information from board: " + board_ids[id - broadcast_id - 1] + " with FW version: "
                             + str(fw_versions[id]))
            except Exception as e:
                # pass
                raise Exception(f"ERR: Could not read FW version: {e}")
            return fw_versions

    def load_mapping(self):
        """
        This function loads the hil project specific signal mapping
        """
        return

    def set_single_relay(self, channel, command, value):
        """
        Sets or resets a command on a specific channel
        :param channel: int: channel number
        :param command: 'oc', 'fr1', 'fr2', 'r12', etc. based on the card
        :param value: bool: set or unset the oc
        """
        [card, signal] = self.get_fib_card(channel)
        # get numer and send command
        data = self.signal_cards[card].get_command_for_msg(signal, command, value)
        self.send_relay_can_message(card, data, channel)

    def set_multiple_relays(self, command, value, pins=None):
        """
        Sets or resets the relays for the list of pins
        :param pins: list of pins
        :param command: str: 'oc', 'fr1', 'fr2', 'r12', etc. based on the card (only one command at a time)
        :param value: bool: True (Set relay) or False (reset relay)
        :return: None
        """
        ssc0_state = 0
        ssc1_state = 0
        ssc2_state = 0
        ssc3_state = 0
        ac_state = 0
        bc_state = 0
        cards = []
        if pins is None and command == 'oc' and value is True:
            self.oc_all_relays(0)
            self.oc_all_relays(1)
            self.oc_all_relays(2)
            self.oc_all_relays(3)
            self.oc_all_relays(4)
            self.oc_all_relays(5)
            logging.info("All pins from 0-59 OC")
        else:
            for channel in pins:
                [card, signal] = self.get_fib_card(channel)
                logging.info(f"Card: {card}, Signal:{signal} ")
                cards.append(card)
                if card == 0:
                    data_ssc0 = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        ssc0_state = ssc0_state | data_ssc0
                    else:
                        ssc0_state = ssc0_state & ~data_ssc0
                    # logging.info(f"Std SC 1 State: {ssc0_state}")
                elif card == 1:
                    data_ssc1 = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        ssc1_state = ssc1_state | data_ssc1
                    else:
                        ssc1_state = ssc1_state & ~data_ssc1
                    # logging.info(f"Std SC 2 State: {ssc1_state}")
                elif card == 2:
                    data_ssc2 = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        ssc2_state = ssc2_state | data_ssc2
                    else:
                        ssc2_state = ssc2_state & ~data_ssc2
                    # logging.info(f"Std SC 3 State: {ssc2_state}")
                elif card == 3:
                    data_ssc3 = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        ssc3_state = ssc3_state | data_ssc3
                    else:
                        ssc3_state = ssc3_state & ~data_ssc3
                    # logging.info(f"Std SC 4 State: {ssc3_state}")
                elif card == 4:
                    data_ac = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        ac_state = ac_state | data_ac
                    else:
                        ac_state = ac_state & ~data_ac
                    # logging.info(f"AC State: {ac_state}")
                elif card == 5:
                    data_bc = self.signal_cards[card].get_command_for_msg(signal, command, value)
                    if value is True:
                        bc_state = bc_state | data_bc
                    else:
                        bc_state = bc_state & ~data_bc
                    # logging.info(f"BC State: {bc_state}")

            data = [ssc0_state, ssc1_state, ssc2_state, ssc3_state, ac_state, bc_state]
            for card in cards:
                self.send_card_can_message(card, data[card])

    def oc_all_relays(self, card):
        """
        Open Circuits all relays on the signal cards (except HV signal card)
        :param card: int:
        """
        logging.info(card)
        # get numer and send command
        if 0 <= card <= 3:
            data = 0b000000000000000000000000000001001001001001000100100100100100
        elif card == 4:
            data = 0b000000000000000001000100000010001000100010001000100010001000
        elif card == 5:
            data = 0b000000000000000000001000100010001000100010001000100010001000

        self.send_card_can_message(card, data)

    def send_card_can_message(self, card, data):
        """
        Creates a can message out of the state and sends it to the can connector for a signal card
        :param card: int: 0-5 for the Signal Cards
        :param data: CAN Message is RC_Cntrl , ID 0x210
        Signals :
            RC_mux -> fib Card (0-7) multiplexer
            RC_cntrlXX -> 60 Bit for the relays XX is multiplexer eg (01 or 00)
        """
        mux_name = "RC_cntrl" + str(card).zfill(2)

        cmd = {"RC_mux": card, mux_name: data}
        self.send_can_message("RC_Cntrl", cmd)

    def send_relay_can_message(self, card, data, channel):
        """
        creates a can message out of the state and sends it to the can connector

        CAN Message is RC_Cntrl , ID 0x210
        Signals :
            RC_mux -> fib Card (0-7) multiplexer
            RC_cntrlXX -> 60 Bit for the relays XX is multiplexer eg (01 or 00)
        """
        mux_name = "RC_cntrl" + str(card).zfill(2)
        cmd = {"RC_mux": card, mux_name: data, "chan": channel}
        self.send_can_message("RC_Cntrl", cmd)

    def send_can_message(self, msg_name, commands):
        try:
            cmd_message = self.can_db.get_message_by_name(msg_name)
        except Exception as e:
            print(f"ERROR: Message {msg_name} not found in Databases")
            print(e)
            return None

        # prepare a message with all signals
        signals = {}
        for signal in cmd_message.signals:
            if signal.name in commands:
                signals[signal.name] = commands[signal.name]
            else:
                signals[signal.name] = 0

        message = can.Message(arbitration_id=cmd_message.frame_id,
                              data=cmd_message.encode(signals, strict=False),
                              is_extended_id=False)
        logging.info(f"sending message {message}")
        self.bus.send(message)

    def get_fib_card(self, channel):
        """
        Calculates the FIB card number for a specific channel
        range 0-39 -> Standard signal card Id 10 steps
        range 40-49 -> Analog Signal card
        range 50-59 -> Bus Signal
        range 60-69 -> HV Signals
        Parameters
        ----------
        channel : int
            the channel to look for

        Returns
        -------
        int
            fib card number starting at 0

        """
        if channel in range(0, 70):
            return [channel // 10, channel % 10]
        else:
            return [-1, -1]


class SignalCard(object):
    """
    Base class for the Signal Cards
    """
    def __init__(self, dbc_dir=os.path.join(os.path.dirname(__file__))+"/dbc/"):
        self.bus = None
        self.can_db = cantools.database.Database()
        self.dbc_dir = dbc_dir
        for file in os.listdir(self.dbc_dir):
            if file.endswith(".dbc"):
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), self.dbc_dir + file))

        self.state = 0
        self.cmd_len = None

    def can_connection(self, interface, channel, bitrate):
        """
        Establishes a CAN connection
        :param interface: this usage with PEAK CAN Dongle
        :param channel: PCAN_USBBUS
        :param bitrate: 500000
        """
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()
        self.bus.flush_tx_buffer()  # Reset transmit after start

    def calculate_bit(self, signal, cmd, value):
        # calculate bit
        bit = cmd << signal * self.cmd_len

        if value:
            return self.state | bit  # make 'or' to switch on
        else:
            return self.state & ~bit  # make 'and' with negated to switch off

    def get_command_for_msg(self, signal, command, value):
        return None

    def send_can_message(self, msg_name, commands):
        try:
            cmd_message = self.can_db.get_message_by_name(msg_name)
        except Exception as e:
            print(f"ERROR: Message {msg_name} not found in Databases")
            print(e)
            return None

        # prepare a message with all signals
        signals = {}
        for signal in cmd_message.signals:
            if signal.name in commands:
                signals[signal.name] = commands[signal.name]
            else:
                signals[signal.name] = 0

        message = can.Message(arbitration_id=cmd_message.frame_id,
                              data=cmd_message.encode(signals, strict=False),
                              is_extended_id=False)
        logging.info(f"sending message {message}")
        self.bus.send(message)

    @staticmethod
    def print_bin(num):
        x = []
        for b in num:
            x.append(bin(b))
        print(x)

    @staticmethod
    def create_payload(card_id, relay_data):
        """
        This will create a list with 8 Data bytes (Total 64 Bits) to control HiL Cards
        Datastructure is as follows: (one based)
        Bit 1-4 -> Card ID
        Bit 5-64 -> Relay Data
        """
        out = [0] * 8
        out[0] = out[0] | (card_id & 0xF)
        out[0] = out[0] | (relay_data & 0xF) << 4
        for i in range(7):
            out[i + 1] = out[i + 1] | ((relay_data >> (i * 8) + 4) & 0xFF)
        return out

    def set_dac_value(self, channel, value):
        """Short summary.
        creates a can message out of the  dac state and sends it to the can connector

        CAN Message is DAC_BMS_Cntrl , ID 0x220
        Be aware of a weird channel mapping
        """
        dac_setpoints[channel] = value
        # Generate Signal name DAC_BMS_Cntrl_XX_YY_Voltage
        channel_msg = dac_mapping[channel] - 1
        dac_no = str(channel_msg // 4 + 1).zfill(2)  # Calculate Dac index, each dac has 4 channels
        ch_no = str((channel_msg % 4) + 1).zfill(2)  # channel is mod 4, both have to be filled to two digits
        mux = (0x10 * (channel_msg // 4)) + (channel_msg % 4)  # mux is 0-3 + 0x10 after each 4 channels
        cmd = {'DAC_BMS_Cntrl_Channel': mux, f"DAC_BMS_Cntrl_{dac_no}_{ch_no}_Voltage": value}
        self.send_can_message("DAC_BMS_Cntrl", cmd)

    def send_relay_can_message(self, card, data):
        mux_name = "RC_cntrl" + str(card).zfill(2)
        cmd = {'RC_mux': card, mux_name: data}
        self.send_can_message("RC_Cntrl", cmd)

    def send_relay_can_message_raw(self, card, data):
        message = can.Message(arbitration_id=528,
                              data=self.create_payload(card, data),
                              is_extended_id=False)
        self.bus.send(message)

    def check_card(self, card, relays=None):
        if card > 16:
            print(f"Card not there: {card}")
            return None
        if relays is None:
            max_relays = [32, 32, 32, 32, 48, 48, 32]  # max relays of cards
            relays = range(max_relays[card])
        if card == 4:  # analog card also set dac
            for ch in range(8):
                self.set_dac_value(ch, 2)
        for relay_no in relays:
            rly_set = 1 << (relay_no)
            print(f"Setting Card {card}, relay {relay_no}")
            print(bin(rly_set))
            self.send_relay_can_message_raw(card, rly_set)
            time.sleep(0.5)
            self.send_relay_can_message_raw(card, 0)
            time.sleep(0.1)


class StandardSignalCard(SignalCard):
    """Short summary.
    Standard Signal card has 10 Signals with the following functions:
        - Short to Chassis (SC)
        - Short to Faultrail
        - Open Circuit to out

    Mapping always signal*3 +
        - 0 for SC
        - 1 for Fault Rail
        - 2 for open circuit
    """

    def __init__(self):
        super().__init__()
        self.state = 0  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 3  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # Calculate command
        if command == "fr2":
            cmd = 0b001
        elif command == "fr1":
            cmd = 0b010
        elif command == "oc":
            cmd = 0b100
        else:
            logging.warning(f"Warning: {command} not accepted")
            return self.state
        logging.info(f"calculated bit {self.calculate_bit(signal, cmd, value)}")
        return self.calculate_bit(signal, cmd, value)


    def calculate_bit(self, signal, cmd, value):
        """
        Standard signal card uses not all channels of expander
        After the first 5 signals we need to shift by one bit
        Therefore shift by one bit if signal >= 5 (zero based )
        """
        bit = cmd << signal * self.cmd_len
        if signal >= 5:
            bit = bit << 1

        if value:
            return self.state | bit  # make 'or' to switch on
        else:
            return self.state & ~bit  # make 'and' with negated to switch off

    def test_standard_signal_card1(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(0, used_ports)

    def test_standard_signal_card2(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(1, used_ports)

    def test_standard_signal_card3(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(2, used_ports)

    def test_standard_signal_card4(self):
        used_ports = list(range(15)) + list(range(16, 31))  # zero based
        self.check_card(3, used_ports)


class AnalogSignalCard(SignalCard):
    """
    Analog Signal card has 8 Signals with the following functions:
        - Short to Fault Rail 2 (FR2)
        - Short to Fault Rail (FR1)
        - Connect DAC Output
        - Open Circuit to out

    And 2 signals that are resistor signals with the following functions:
        - Short to Chassis (FR2)
        - Short to Fault Rail (FR1)
        - Resistor 12R
        - Resistor 24R
        - Resistor 51R
        - Resistor 100R
        - Open Circuit to out

    Mapping always signal*4 +
        - 0 for FR2
        - 1 for Fault Rail FR1
        - 2 for Connect dac
        - 3 for open circuit
    """

    def __init__(self):
        super().__init__()
        self.bus = self.bus
        self.state = 0  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 4  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            logging.warning(f"Warning: Channel {signal} in command not accepted")
            return self.state

        elif command == "dac_voltage":
            if signal in range(0, 7):
                self.set_dac_value(signal, float(value))
                return self.state
        # Calculate command
        elif signal in range(0, 8):
            if command == "fr2":
                cmd = 0b0001
            elif command == "fr1":
                cmd = 0b0010
            elif command == "dac":
                cmd = 0b0100
            elif command == "oc":
                cmd = 0b1000
        elif signal in range(8, self.signals):
            if command == "fr2":
                cmd = 0b0000001
            elif command == "fr1":
                cmd = 0b0000010
            elif command == "r12":
                cmd = 0b0000100
            elif command == "r24":
                cmd = 0b0001000
            elif command == "r51":
                cmd = 0b0010000
            elif command == "r100":
                cmd = 0b0100000
            elif command == "oc":
                cmd = 0b1000000
        else:
            logging.warning(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)

    def test_analog_signal_card(self):
        used_ports = list(range(39)) + list(range(40, 48))  # zero based
        self.check_card(4, used_ports)


class BusSignalCard(SignalCard):
    """
    Bus Signal card has 12 Signals with the following functions:
        - Fault Rail 2 (First Bit)
        - Fault Rail 1 (second Bit)
        - Additional Input (third bit)
        - Open Circuit (fourth bit)
    On FIB boot up, in the Bus Signal card, the relays 3 & 4 are NO by software instead of NC (default for other cards)
    This is to facilitate the CAN H and CAN L connections to the DSUB-9 connector going to the load box, usually in a HiL.
    """

    def __init__(self):
        super().__init__()
        self.bus = self.bus
        self.state = 0  # Todo get initial state from status message
        self.signals = 12
        self.cmd_len = 4  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        cmd = {}
        # Check if channel is in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # calculate command
        elif signal in range(0, self.signals):
            if command == "fr2":
                cmd = 0b0001
            elif command == "fr1":
                cmd = 0b0010
            elif command == "in":
                cmd = 0b0100
            elif command == "oc":
                cmd = 0b1000
        else:
            print(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)

    def test_bus_signal_card(self):
        used_ports = list(range(3 * 16))  # zero based
        self.check_card(5, used_ports)


class HVSignalCard(SignalCard):
    """
    HV Signal card has 8 HV Signals with the following functions:
        - Short to Chassis (SC) via resistor
        - Open Circuit
    There are also 2 Channels for ISOSPI Connection which allow Open Circuit
    Channel 1-8 -> HV
    Channel 9,10 -> ISOSPI
    """

    def __init__(self):
        super().__init__()
        # Initial State is complicated. All first 16 Bits are 'on'
        # On the second 16 Bit we need to switch on only every second
        self.bus = self.bus
        self.state = int(b"01010101010101011111111111111111", 2)  # Todo get initial state from status message
        self.signals = 10
        self.cmd_len = 2  # amount of usable functions on card
        return

    def get_command_for_msg(self, signal, command, value):
        # Check if channel in range
        if signal >= self.signals:
            print(f"Warning: Channel {signal} in command not accepted")
            return self.state

        # Calculate command
        if command == "oc":
            cmd = 0b01
        elif command == "sc":
            cmd = 0b10
        else:
            print(f"Warning: {command} not accepted")
            return self.state
        return self.calculate_bit(signal, cmd, value)


    def calculate_bit(self, signal, cmd, value):
        """
        HV signal card uses not all channels of expander the first expander
        is connected to ISOSPI channels. second one is for HV Signals
        Therefore shift by 16 bits if signal <8 (zero based )
        """
        if signal >= 8:
            bit = cmd << ((signal - 8) * self.cmd_len)
        else:
            bit = cmd << ((signal * self.cmd_len) + 16)

        # HV OC Signals are reed relays and need and are inverted -> On is not SC, Off is SC
        # HV SC Signals are not inverted, so we need to distinguish
        if value:
            if cmd == 0b01:
                return self.state & ~bit  # make 'or' to switch on
            else:
                return self.state | bit  # make 'or' to switch on
        else:
            if cmd == 0b01:
                return self.state | bit  # make 'and' with negated to switch off
            else:
                return self.state & ~bit  # make 'and' with negated to switch off

    def test_hv_signal_card(self):
        used_ports = list(range(4)) + list(range(16, 32))  # zero based
        self.check_card(6, used_ports)
