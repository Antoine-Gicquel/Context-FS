#!/usr/bin/env python3

from fuse import FUSE, FuseOSError, Operations
from errno import ENOENT, EACCES
import os
import time

class CtxFS(Operations):
	def __init__(self, _origin):
		self.origin = _origin
		self.global_context = []
		self.global_context_file = "/context"
		self.wrapped_folder = "/wrapped"
		self.uid = os.getuid()
		self.gid = os.getgid()

	def set_origin(self, orig):
		self.origin = orig

	def add_context(self, L):
		for word in L:
			if len(word)>0:
				self.global_context.append(word.strip(b'\n \t\r'))
		print("Context is now", self.global_context)

	def is_wrapped_file(self, path):
		if path.startswith(self.wrapped_folder + "/"):
			p = path[len(self.wrapped_folder + "/"):]
			return os.path.isfile(os.path.join(self.origin, p))
		return False

	def is_wrapped_folder(self, path):
                if path.startswith(self.wrapped_folder + "/"):
                        p = path[len(self.wrapped_folder + "/"):]
                        return os.path.isdir(os.path.join(self.origin, p))
                return False

	def list_wrapped_folder(self, path):
		if path.startswith(self.wrapped_folder + "/"):
			p = path[len(self.wrapped_folder + "/"):]
			return os.listdir(os.path.join(self.origin, p))
		raise FuseOSError(ENOENT)

	def read_wrapped_file(self, path):
		if path.startswith(self.wrapped_folder + "/"):
			p = path[len(self.wrapped_folder + "/"):]
			c = b'\n'.join(self.global_context)
			if len(c) > 0:
				c += b'\n'
			with open(os.path.join(self.origin, p), 'rb') as f:
				c += f.read()
			return c
		raise FuseOSError(ENOENT)

	def get_wrapped_file_size(self, path):
		return len(self.read_wrapped_file(path))

	# Filesystem methods
	def getattr(self, path, fh=None):
		print("getattr", path, fh)
		if path == '/':
			return {'st_mode': 0o40755, 'st_nlink': 2, 'st_size': 4096, 'st_uid': self.uid, 'st_gid': self.gid}
		if path == self.global_context_file:
			return {'st_mode': 0o100644, 'st_size': len(b'\n'.join(self.global_context)) + int(len(self.global_context)>0), 'st_uid': self.uid, 'st_gid': self.gid}
		if path == self.wrapped_folder:
			return {'st_mode': 0o40755, 'st_nlink': 2, 'st_size': 4096, 'st_uid': self.uid, 'st_gid': self.gid}
		if self.is_wrapped_folder(path):
			return {'st_mode': 0o40755, 'st_nlink': 2, 'st_size': 4096, 'st_uid': self.uid, 'st_gid': self.gid}
		if self.is_wrapped_file(path):
			return {'st_mode': 0o100444, 'st_size': self.get_wrapped_file_size(path), 'st_uid': self.uid, 'st_gid': self.gid}
		raise FuseOSError(ENOENT)

	def readdir(self, path, fh):
		print("readdir", path, fh)
		if path == "/":
			return ['.', '..', self.wrapped_folder.lstrip('/'), self.global_context_file.lstrip('/')]
		if path == self.wrapped_folder:
			return ['.', '..'] + os.listdir(self.origin)
		if self.is_wrapped_folder(path):
			return ['.', '..'] + self.list_wrapped_folder(path)
		raise FuseOSError(ENOENT)

	def read(self, path, size, offset, fh):
		print("read", path, size, offset, fh)
		if path == self.global_context_file:
			context_string = b"\n".join(self.global_context)
			if len(context_string) > 0:
				context_string += b'\nzeub\n'
			return context_string
		if self.is_wrapped_file(path):
			return self.read_wrapped_file(path)
		raise FuseOSError(ENOENT)

	def write(self, path, data, offset, fh):
		if path == self.global_context_file:
			self.add_context(data.split(b'\n'))
			return len(data)
		else:
			raise FuseOSError(ENOENT)

	def open(self, path, flags):
		print("open", path, flags)
		return 0

	def create(self, path, mode, fh=None):
		print("create", path, mode, fh)
		if path == self.global_context_file:
			return 0
		else:
			raise FuseOSError(ENOENT)

	def truncate(self, path, length, fh=None):
		print("truncate")
		return 0

def main(mountpoint, origin):
	FUSE(CtxFS(origin), mountpoint, nothreads=True, foreground=True, ro=False)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('origin', help='Folder to wrap with context')
	parser.add_argument('mountpoint', help='Directory to mount the wrapping filesystem')
	args = parser.parse_args()
	main(args.mountpoint, args.origin)
