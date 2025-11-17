# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class MNPackageQuote(Document):
	def validate(self):
		"""Set cache expiry"""
		if not self.expires_at:
			# Cache expires in 1 hour by default
			self.expires_at = frappe.utils.add_to_date(frappe.utils.now(), hours=1)

		# Calculate price range and total from items
		if self.items:
			prices_min = [item.total_price_min for item in self.items if item.total_price_min]
			prices_max = [item.total_price_max for item in self.items if item.total_price_max]

			if prices_min:
				self.price_range_min = min(prices_min)
			if prices_max:
				self.price_range_max = max(prices_max)

			self.total_packages = len(self.items)

	def is_expired(self):
		"""Check if cache is expired"""
		if self.status == "Expired":
			return True

		if self.expires_at:
			now = frappe.utils.now_datetime()
			expires = frappe.utils.get_datetime(self.expires_at)
			if now > expires:
				self.status = "Expired"
				self.save()
				return True

		return False

	@frappe.whitelist()
	def create_pre_order(self, hotel, board, room_type=None):
		"""
		Create a pre-order from this quote for specific hotel and board.
		"""
		if self.is_expired():
			frappe.throw(_("This quote has expired. Please search again."))

		# Find the matching item
		matching_item = None
		for item in self.items:
			if item.hotel == hotel and item.board == board:
				if room_type and item.room_type != room_type:
					continue
				matching_item = item
				break

		if not matching_item:
			frappe.throw(_("Hotel and board combination not found in quote"))

		# Get search details
		search = frappe.get_doc("MN Package Search", self.package_search)

		# Create pre-order
		pre_order = frappe.get_doc({
			"doctype": "MN Pre Order",
			"package_quote": self.name,
			"package_search": self.package_search,
			"agent": search.agent,
			"customer": search.customer,
			"hotel": hotel,
			"room_type": room_type or matching_item.room_type,
			"board": board,
			"date_from": self.date_from,
			"date_to": self.date_to,
			"nights": self.nights,
			"adults": self.adults,
			"children": self.children,
			"hotel_price": matching_item.hotel_price_min,  # Use min price
			"transfer_price": matching_item.transfer_price or 0,
			"additional_services_price": matching_item.additional_services_price or 0,
			"total_price": matching_item.total_price_min,
			"status": "Pending"
		})
		pre_order.insert()

		return pre_order.name
