"""
  High Level Computer functions

  npy

"""

import os
import os.path
import socket
from nwebclient import util
from nwebclient import runner


def get_ip():
    return socket.gethostbyname(socket.gethostname())

def udp_send(data, ip='255.255.255.255', port=4242):
    sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM,  socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data.encode('ascii'), (ip, port))

def system(args):
    help_system()
    args.dispatch(
        bluetooth_serial_enable=lambda args: system_bluetooth_serial_enable(args)
    )

def system_exec(cmd):
    print("Executing: " + cmd)
    os.system(cmd)


def system_bluetooth_serial_enable(args):
    print("")
    f = '/etc/systemd/system/dbus-org.bluez.service'
    print("Configure: " + f);
    if not os.path.isfile(f):
        print("Bluetooth Config not exists. File: " + f)
        return;
    os.system(f"cp {f} {f}.bak")
    lines = util.file_get_lines(f)
    def line_transform(line):
        if line.startswith('ExecStart='):
            return 'ExecStart=/usr/lib/bluetooth/bluetoothd -C\nExecStartPost=/usr/bin/sdptool add SP'
        else:
            return line
    lines = map(line_transform, lines)
    util.file_put_contents(f, '\n'.join(lines))
    print("Config rewrite done.")
    system_exec("systemctl daemon-reload")
    system_exec("systemctl restart bluetooth.service")
    system_exec("bluetoothctl discoverable on")
    print("")
    print(" Verify: sudo service bluetooth status")
    print(" Usage: nwebclient.runner:BluetoothSerial")
    # sudo rfcomm watch hci0


class Bluetooth(runner.BaseJobExecutor):
    def execute(self, data):
        from bluetooth import discover_devices
        nearby_devices = discover_devices(lookup_names=True)
        devices = []
        for name, addr in nearby_devices:
            devices.append({"name": name, "addr": addr})
        return {'sucess': True, 'devices': devices}


class NxSystemRunner(runner.LazyDispatcher):
    def __init__(self):
        super().__init__('type', bt_scan=Bluetooth())


def help_system():
    print("npy system - Linux System Configuration")
    print("")
    print("  sudo npy system bluetooth-serial-enable")
    print("")
    print("sudo required")


def help():
    print('Usage: ')
    print('  npy send_ip')
    print('  npy ip')
    print('')
    print('Tipps:')
    print('  Cron-Job')
    print('    */10  * * * * npy send_ip')
    print('')
    help_system()


def main():
    args = util.Args()
    args.shift()
    if args.help_requested():
        return help()
    else:
        r = NxSystemRunner()
        if args.hasShortFlag('send_ip') or args.hasName('send_ip'):
            udp_send('nxudp npy' + str(get_ip()) + " from-npy")
        elif args.hasShortFlag('ip') or args.hasName('ip'):
            print(get_ip())
        elif r.support_type(args.first()):
            args.cfg = {'type': args.first()}
            res = r.execute(args)
            print(r.to_text(res))
        else:
            args.dispatch(
                system=system,
                help=lambda: help()
            )


if __name__ == '__main__':
    main()
