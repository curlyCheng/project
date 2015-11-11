import mmh3
from bitarray import bitarray

class BloomFilter(object):
	"""docstring for BloomFilter"""
	def __init__(self, size, elem_count):
		self.hash_count = int(0.7*(size/elem_count))
		self.bit_arr = bitarray(size)
		self.bit_arr.setall(0)
		self.size = size
		print "%0.20f%%" %0.6185**(size/elem_count)
	def add(self, elem):
		for x in xrange(self.hash_count):
			index = mmh3.hash(elem, x) % self.size
			self.bit_arr[index] = 1
	def in_bf(self, elem):
		for x in xrange(self.hash_count):
			index = mmh3.hash(elem, x) % self.size
			if (self.bit_arr[index] == 0):
				return False
		return True
			