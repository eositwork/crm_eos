# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class MNPackageSearch(Document):
	def validate(self):
		"""Validate and calculate date_to"""
		if self.date_from and self.nights:
			from_date = frappe.utils.getdate(self.date_from)
			self.date_to = frappe.utils.add_days(from_date, self.nights)

		if not self.agent:
			self.agent = frappe.session.user

	def before_save(self):
		"""Set search date"""
		if not self.search_date:
			self.search_date = frappe.utils.now()

	@frappe.whitelist()
	def execute_search(self):
		"""
		Execute package search and create/update MN Package Quote.
		Returns price range and total packages found.
		"""
		self.status = "Searching"
		self.save()

		# Import here to avoid circular dependency
		from mn_hotel_rates.mn_hotel_rates.api.package_search import search_packages

		result = search_packages(self.name)

		self.price_range_min = result.get('price_range_min', 0)
		self.price_range_max = result.get('price_range_max', 0)
		self.total_packages_found = result.get('total_packages', 0)
		self.status = "Completed"
		self.save()

		return result
