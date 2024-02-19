#!./runmodule.sh

import os
import subprocess
import shlex
import re
import dataclasses
import typing

from confattr import Config, UiNotifier
from confattr.types import Regex


class Path:

	type_name = 'path'
	help = '''
	The path to a directory.
	You can use "~/" as an abbreviation for your home directory.
	The path may start with "UUID:.../", then the file system is mounted automatically.
	If the file system is on an encrypted partition you can use "UNLOCK:...,UUID:.../".
	'''

	def __init__(self, value: str) -> None:
		self.raw = value

	def __str__(self) -> str:
		return self.raw

	def __repr__(self) -> str:
		return '%s(%r)' % (type(self).__name__, self.raw)


FILESYSTEM_TYPE_FAT = 'vfat'
FILESYSTEM_TYPE_EXT4 = 'ext4'
FILESYSTEM_TYPE_SWAP = 'swap'
FILESYSTEM_TYPE_LVM2 = 'LVM2_member'
FILESYSTEM_LUKS = 'crypto_LUKS'

DEVICE_TYPE_DISK = 'disk'
DEVICE_TYPE_PARTITION = 'part'
DEVICE_TYPE_CRYPT = 'crypt'
DEVICE_TYPE_LVM = 'lvm'


def shlex_join(cmd: typing.Sequence[str]) -> str:
	return ' '.join(shlex.quote(w) for w in cmd)


mounted_devices: typing.Set['Device'] = set()


@dataclasses.dataclass
class Device:

	path: str
	fstype: str
	uuid: str
	mountpoint: str
	type: str

	label: str
	partlabel: str
	vendor: str
	model: str
	size: str

	def __post_init__(self) -> None:
		self.vendor = self.vendor.strip()

	def __hash__(self) -> int:
		return hash(self.path)

	@classmethod
	def from_uuid(cls, uuid: str) -> 'Device':
		for dev in lsblk.iter_devices():
			if dev.uuid == uuid:
				return dev

		raise SubprocessException('Failed to find device with file system UUID %r' % uuid)

	@classmethod
	def from_path(cls, path: str) -> 'Device':
		devices = tuple(lsblk.iter_all_devices(path, nodeps=True))
		n = len(devices)
		if n == 0:
			raise SubprocessException('No device %r' % path)
		elif n == 1:
			return devices[0]
		else:
			raise SubprocessException('Found several devices with path %r' % path)

	def is_encrypted(self) -> bool:
		return self.fstype == FILESYSTEM_LUKS

	def is_unlocked(self) -> bool:
		return len(lsblk.get_uuids(self.path)) > 1

	def is_mounted(self) -> bool:
		return bool(self.mountpoint)

	def get_name(self) -> str:
		if self.label:
			return self.label
		elif self.partlabel:
			return self.partlabel
		elif self.vendor or self.model:
			return '%s %s' % (self.vendor, self.model)
		else:
			return self.path

	def get_uuid_based_path(self) -> str:
		if self.uuid:
			path = ''
			crypto_backing_device_uuid = udisksctl.get_crypto_backing_device_uuid(self.path)
			if crypto_backing_device_uuid:
				path += Mounter.PREFIX_UNLOCK + crypto_backing_device_uuid + Mounter.PREFIX_SEP
			path += Mounter.PREFIX_UUID + self.uuid
			if self.mountpoint.endswith(os.path.sep):
				path += os.path.sep
			return path

		return self.mountpoint

	def get_crypto_backing_device(self) -> typing.Optional['Device']:
		crypto_backing_device_path = udisksctl.get_crypto_backing_device_path(self.path)
		if crypto_backing_device_path is None:
			return None
		return self.from_path(crypto_backing_device_path)


	def unlock(self) -> 'Device':
		path = udisksctl.unlock(self.path)
		return self.from_path(path)

	def mount(self) -> None:
		self.mountpoint = udisksctl.mount(self.path)
		mounted_devices.add(self)

	def unmount(self) -> None:
		udisksctl.unmount(self.path)
		self.mountpoint = ''
		mounted_devices.remove(self)

	def lock(self) -> None:
		udisksctl.lock(self.path)


class Mounter:

	PREFIX_UNLOCK = 'UNLOCK:'
	PREFIX_UUID = 'UUID:'
	PREFIX_SEP = ','

	def mount_path_if_necessary(self, path: typing.Union[str, Path], password_entry_context: typing.ContextManager[None]) -> typing.Optional['Device']:
		i1: typing.Optional[int]

		if isinstance(path, Path):
			path = path.raw

		if path.startswith(self.PREFIX_UNLOCK):
			sep = self.PREFIX_SEP + self.PREFIX_UUID
			i0 = len(self.PREFIX_UNLOCK)
			i1 = path.find(sep)
			if i1 < 0:
				raise SubprocessException(f'invalid path {path!r}: missing {sep!r} after {self.PREFIX_UNLOCK!r}')
			uuid = path[i0:i1]
			dev = Device.from_uuid(uuid)
			if not dev.is_unlocked():
				with password_entry_context:
					dev.unlock()
			i0 = i1 + len(self.PREFIX_SEP)
			path = path[i0:]

		elif not path.startswith(self.PREFIX_UUID):
			return None

		i0 = len(self.PREFIX_UUID)
		i1 = path.find(os.path.sep)
		if i1 < 0:
			i1 = None
		uuid = path[i0:i1]
		dev = Device.from_uuid(uuid)
		if not dev.is_mounted():
			dev.mount()
		return dev

	def expand_path(self, path: typing.Union[str, Path], password_entry_context: typing.ContextManager[None]) -> str:
		if isinstance(path, Path):
			path = path.raw

		dev = self.mount_path_if_necessary(path, password_entry_context)
		if dev:
			try:
				return dev.mountpoint + path[path.index(os.path.sep):]
			except ValueError:
				return dev.mountpoint
		return os.path.expanduser(path)



class SubprocessException(Exception):

	def __str__(self) -> str:
		out = super().__str__()
		if self.args and isinstance(self.args[0], subprocess.CalledProcessError):
			err = self.args[0].stderr
			if isinstance(err, bytes):
				err = err.decode()
			out += '\n' + err.rstrip()
		return out


class Lsblk:

	device_paths_to_be_ignored: typing.ClassVar = Config('devices-to-be-ignored', ['/dev/sda'],
		help='in the wizard to create a new backup plan these devices are not displayed when selecting the source/destination path')
	file_system_types_to_be_ignored = Config('file-system-types-to-be-ignored', [FILESYSTEM_TYPE_SWAP, FILESYSTEM_TYPE_LVM2],
		help='in the wizard to create a new backup plan filesystems with these types are not displayed when selecting the source/destination path')

	# ------- init -------

	def __init__(self) -> None:
		self.uuids_to_be_ignored = self.get_uuids(*self.device_paths_to_be_ignored)

	def get_uuids(self, *paths: str) -> typing.Sequence[str]:
		if not paths:
			return []

		cmd = ['lsblk', '-n', '-o', 'UUID'] + list(paths)
		try:
			p = subprocess.run(cmd, capture_output=True, text=True)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)
		return p.stdout.splitlines()

	def iter_all_devices(self, *paths: str, nodeps: bool = False) -> typing.Iterator[Device]:
		cmd = ['lsblk', '-n', '--pairs', '-o', 'PATH,FSTYPE,UUID,MOUNTPOINT,TYPE,LABEL,PARTLABEL,SIZE,VENDOR,MODEL']
		if nodeps:
			cmd.append('--nodeps')
		cmd.extend(paths)
		try:
			p = subprocess.run(cmd, capture_output=True, text=True, check=True)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)
		for ln in p.stdout.splitlines():
			args = dict(self.split_pair(v) for v in shlex.split(ln))
			yield Device(**args)

	def iter_devices(self, *paths: str) -> typing.Iterator[Device]:
		# I have seen a disk and a partition on it having the same values (UUID, FSTYPE, LABEL)
		# on a Debian and Arch install stick where the partition was mountable but the disk was not.
		# Therefore I am ignoring all disks which have the same UUID like a partition.
		devices: typing.Dict[str, Device] = {}
		devices_without_uuid = []
		for dev in self.iter_all_devices(*paths):
			if not dev.uuid:
				devices_without_uuid.append(dev)
			elif dev.uuid in devices:
				dev2 = devices[dev.uuid]
				if dev.type == DEVICE_TYPE_PARTITION and dev2.type == DEVICE_TYPE_DISK:
					devices[dev.uuid] = dev
				elif dev2.type == DEVICE_TYPE_PARTITION and dev.type == DEVICE_TYPE_DISK:
					pass
				else:
					raise SubprocessException(f'{dev.path} has the same UUID like {dev2.path}')
			else:
				devices[dev.uuid] = dev
		yield from devices_without_uuid
		yield from devices.values()

	@staticmethod
	def split_pair(key_val: str) -> typing.Tuple[str, str]:
		key, val = key_val.split('=', 1)
		key = key.lower()
		return key, val

	def iter_interesting_devices(self) -> typing.Iterator[Device]:
		for dev in self.iter_devices():
			if dev.uuid in self.uuids_to_be_ignored:
				continue
			if not dev.fstype:
				continue
			if dev.fstype in self.file_system_types_to_be_ignored:
				continue
			if dev.is_encrypted() and dev.is_unlocked():
				continue
			yield dev

	def iter_mounted_devices(self) -> typing.Iterator[Device]:
		for dev in self.iter_interesting_devices():
			if dev.is_mounted():
				yield dev

	def iter_unmounted_devices(self) -> typing.Iterator[Device]:
		for dev in self.iter_interesting_devices():
			if not dev.is_mounted():
				yield dev


class Udisksctl:

	re_mount_output = Config('udisksctl.mount-output-pattern', Regex(r'^.*?(?P<mountpath>/(\S+/)*[^/]+?)\.?$'),
		help='a regular expression to parse the output of `udisksctl mount`. Must contain a named group called "mountpath".')
	re_unlock_output = Config('udisksctl.unlock-output-pattern', Regex(r'^.*?(?P<unlockpath>/(\S+/)*[^/]+?)\.?$'),
		help='a regular expression to parse the output of `udisksctl unlock`. Must contain a named group called "unlockpath".')

	logger: typing.Optional[UiNotifier] = None

	def set_logger(self, logger: UiNotifier) -> None:
		self.logger = logger

	def remove_logger(self) -> None:
		self.logger = None


	def unlock(self, device_path: str) -> str:
		'''this must be called outside of the urwid main loop because it writes to and reads from the terminal'''
		if self.logger:
			self.logger.show_info('unlocking %s' % device_path)
		print('unlocking %s' % device_path)
		cmd = ['udisksctl', 'unlock', '-b', device_path]
		try:
			p = subprocess.run(cmd, capture_output=True, text=True, check=True)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)
		m = self.re_unlock_output.match(p.stdout)
		if not m:
			raise SubprocessException('Failed to parse the output of `{cmd}`: {out!r}\nExpected pattern: {pattern!r}'.format(
				cmd = shlex_join(cmd), out = p.stdout, pattern = self.re_unlock_output.pattern))

		path = m.group('unlockpath')
		if not os.path.exists(path):
			raise SubprocessException('Misinterpreted output of `{cmd}`, {path!r} does not exist.\nOutput: {out!r}\nExpected pattern: {pattern!r}'.format(
				cmd = shlex_join(cmd), out = p.stdout, pattern = self.re_unlock_output.pattern, path = path))

		return path

	def mount(self, device_path: str) -> str:
		if self.logger:
			self.logger.show_info('mounting %s' % device_path)
		cmd = ['udisksctl', 'mount', '-b', device_path]
		try:
			p = subprocess.run(cmd, capture_output=True, text=True, check=True)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)
		m = self.re_mount_output.match(p.stdout)
		if not m:
			raise SubprocessException('Failed to parse the output of `{cmd}`: {out!r}\nExpected pattern: {pattern!r}'.format(
				cmd = shlex_join(cmd), out = p.stdout, pattern = self.re_mount_output.pattern))

		path = m.group('mountpath')
		if not os.path.isdir(path):
			raise SubprocessException('Misinterpreted output of `{cmd}`, {path!r} is not a directory.\nOutput: {out!r}\nExpected pattern: {pattern!r}'.format(
				cmd = shlex_join(cmd), out = p.stdout, pattern = self.re_mount_output.pattern, path = path))

		return path

	def unmount(self, device_path: str) -> None:
		if self.logger:
			self.logger.show_info('unmounting %s' % device_path)
		cmd = ['udisksctl', 'unmount', '-b', device_path]
		try:
			subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)

	def lock(self, device_path: str) -> None:
		if self.logger:
			self.logger.show_info('locking %s' % device_path)
		cmd = ['udisksctl', 'lock', '-b', device_path]
		try:
			subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)


	def get_crypto_backing_device_path(self, device_path: str) -> typing.Optional[str]:
		return self.get_crypto_backing_device_value(device_path, 'PreferredDevice')

	def get_crypto_backing_device_uuid(self, device_path: str) -> typing.Optional[str]:
		return self.get_crypto_backing_device_value(device_path, 'IdUUID')

	def get_crypto_backing_device_value(self, device_path: str, key: str) -> typing.Optional[str]:
		objpath = self.get_value(device_path, 'CryptoBackingDevice')
		objpath = objpath.strip("'")
		if objpath == '/':
			return None

		return self.get_value(objpath, key, from_object_path=True)

	def get_value(self, path: str, key: str, *, from_object_path: bool = False) -> str:
		prefix = '/org/freedesktop/UDisks2/'
		if from_object_path:
			id_type = '-p'
			if path.startswith(prefix):
				path = path[len(prefix):]
		else:
			id_type = '-b'
		cmd = ['udisksctl', 'info', id_type, path]
		try:
			p = subprocess.run(cmd, capture_output=True, text=True, check=True)
		except (FileNotFoundError, subprocess.CalledProcessError) as e:
			raise SubprocessException(e)

		prefix = key + ':'
		for ln in p.stdout.splitlines():
			ln = ln.strip()
			if ln.startswith(prefix):
				return ln[len(prefix):].strip()

		raise SubprocessException(f'{path} has no information called {key!r}')


lsblk = Lsblk()
udisksctl = Udisksctl()
mounter = Mounter()


if __name__ == '__main__':
	devices = list(lsblk.iter_interesting_devices())
	print('mounted')
	print('-------')
	for dev in devices:
		if dev.is_mounted():
			print('- %s' % dev.get_name())

	print('')
	print('unmounted')
	print('---------')
	for dev in devices:
		if not dev.is_mounted():
			print('- %s' % dev.get_name())
