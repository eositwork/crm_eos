# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MNRateLedger(Document):
	def validate(self):
		"""Validate ledger entry"""
		if self.quantity and self.unit_price_used:
			self.total_row_amount = self.quantity * self.unit_price_used
