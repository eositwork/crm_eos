# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MNRate(Document):
	pass


@frappe.whitelist()
def get_applicable_rate(service_type, service_ref, room_type_ref, board, date_from, date_to,
						occupancy_class="Base", channel="B2B-NET"):
	"""
	Search for applicable rate based on criteria.
	Returns the highest priority rate that matches.
	"""
	filters = {
		"service_type": service_type,
		"service_ref": service_ref,
		"room_type_ref": room_type_ref,
		"board": board,
		"occupancy_class": occupancy_class,
		"channel": channel,
		"stop_sale": 0
	}

	rates = frappe.get_all("MN Rate",
		filters=filters,
		fields=["name", "net_price", "gross_price", "priority", "date_from", "date_to",
				"min_length_of_stay", "release_days"],
		order_by="priority desc, date_from asc"
	)

	# Filter by date overlap
	matching_rates = []
	for rate in rates:
		if rate.date_from <= date_from and rate.date_to >= date_to:
			matching_rates.append(rate)

	if matching_rates:
		return matching_rates[0]
	else:
		return None
