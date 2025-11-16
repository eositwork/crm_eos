# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class MNSpecialOffer(Document):
	def validate(self):
		"""Validate special offer"""
		if self.stay_date_to and self.stay_date_from:
			if self.stay_date_to < self.stay_date_from:
				frappe.throw(_("Stay Date To must be after Stay Date From"))

	@frappe.whitelist()
	def publish_offer_rates(self):
		"""
		Publish this special offer as high-priority MN Rate records.
		"""
		if self.status != "Active":
			frappe.throw(_("Offer must be Active to publish rates"))

		# Delete existing rates from this offer
		frappe.db.delete("MN Rate", {
			"source": "special_offer",
			"source_special_offer": self.name
		})

		rates_created = 0

		# Get base contract rates that this offer applies to
		filters = {
			"date_from": ["<=", self.stay_date_to],
			"date_to": [">=", self.stay_date_from],
			"source": "contract"
		}

		if self.applies_to_room_types:
			room_types = [x.strip() for x in self.applies_to_room_types.split(",")]
			filters["room_type_ref"] = ["in", room_types]

		if self.applies_to_boards:
			boards = [x.strip() for x in self.applies_to_boards.split(",")]
			filters["board"] = ["in", boards]

		base_rates = frappe.get_all("MN Rate",
			filters=filters,
			fields=["*"]
		)

		for base_rate in base_rates:
			# Calculate discounted price
			if self.discount_type == "Percent":
				discounted_price = base_rate.net_price * (1 - self.discount_value / 100.0)
			else:  # Fixed
				discounted_price = base_rate.net_price - self.discount_value

			# Create special offer rate
			offer_rate = frappe.get_doc({
				"doctype": "MN Rate",
				"service_type": base_rate.service_type,
				"service_ref": base_rate.service_ref,
				"room_type_ref": base_rate.room_type_ref,
				"region_district": base_rate.region_district,
				"city": base_rate.city,
				"date_from": max(base_rate.date_from, self.stay_date_from),
				"date_to": min(base_rate.date_to, self.stay_date_to),
				"board": base_rate.board,
				"occupancy_class": base_rate.occupancy_class,
				"uom": base_rate.uom,
				"per": base_rate.per,
				"is_supplement": base_rate.is_supplement,
				"rate_type": "Special",
				"channel": base_rate.channel,
				"base_cost": discounted_price,
				"net_price": discounted_price,
				"gross_price": discounted_price * 1.15,
				"margin_pct": 15,
				"release_days": base_rate.release_days,
				"min_length_of_stay": base_rate.min_length_of_stay,
				"stop_sale": 0,
				"priority": self.priority,
				"source": "special_offer",
				"source_special_offer": self.name,
				"effective_from": self.stay_date_from,
				"effective_to": self.stay_date_to
			})
			offer_rate.insert(ignore_permissions=True)
			rates_created += 1

		frappe.db.commit()
		frappe.msgprint(_("Published {0} special offer rates").format(rates_created))
		return rates_created
