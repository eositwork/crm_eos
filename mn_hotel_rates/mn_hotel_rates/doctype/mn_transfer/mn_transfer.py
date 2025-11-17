# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MNTransfer(Document):
	def get_price(self, passengers=1):
		"""Calculate transfer price based on pricing model"""
		if self.price_per_transfer:
			return self.price_per_transfer
		elif self.price_per_person:
			return self.price_per_person * passengers
		else:
			return 0
