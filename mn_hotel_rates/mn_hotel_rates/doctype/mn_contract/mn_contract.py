# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class MNContract(Document):
	def validate(self):
		"""Validate contract data"""
		self.validate_periods()
		self.validate_effective_dates()

	def validate_periods(self):
		"""Check for overlapping periods"""
		periods = sorted(self.periods, key=lambda p: p.date_from)
		for i in range(len(periods) - 1):
			if periods[i].date_to >= periods[i+1].date_from:
				frappe.throw(_("Periods {0} and {1} overlap").format(
					periods[i].label, periods[i+1].label))

	def validate_effective_dates(self):
		"""Ensure effective_to is after effective_from"""
		if self.effective_to and self.effective_from:
			if self.effective_to < self.effective_from:
				frappe.throw(_("Effective To must be after Effective From"))

	@frappe.whitelist()
	def generate_rates(self):
		"""
		Compile contract data into MN Rate records.
		Called via button "Generate/Republish Rates"
		"""
		if self.status != "Active":
			frappe.throw(_("Contract must be Active to generate rates"))

		# Delete existing rates from this contract
		frappe.db.delete("MN Rate", {
			"service_ref": self.hotel,
			"source": "contract",
			"source_contract": self.name
		})

		rates_created = 0

		# Generate base rates from tariffs
		for tariff in self.tariffs:
			period = self.get_period_by_label(tariff.period)
			room_type = self.get_room_type_by_label(tariff.room_type)

			if not period or not room_type:
				frappe.msgprint(_("Skipping tariff - period or room type not found: {0}").format(
					tariff.period + " / " + tariff.room_type))
				continue

			# Get hotel details for region/city
			hotel_doc = frappe.get_doc("Hotel", self.hotel)

			# Base rate
			base_rate = self.create_rate_record(
				period=period,
				room_type=room_type,
				tariff=tariff,
				hotel_doc=hotel_doc,
				occupancy_class="Base",
				base_cost=tariff.unit_price_net
			)
			base_rate.insert(ignore_permissions=True)
			rates_created += 1

			# Generate occupancy variant rates
			rates_created += self.generate_occupancy_rates(
				period, room_type, tariff, hotel_doc, base_cost=tariff.unit_price_net)

		# Generate supplement rates
		for supplement in self.supplements:
			rates_created += self.generate_supplement_rates(supplement)

		frappe.db.commit()
		frappe.msgprint(_("Generated {0} rate records").format(rates_created))
		return rates_created

	def get_period_by_label(self, label):
		"""Get period row by label"""
		for period in self.periods:
			if period.label == label:
				return period
		return None

	def get_room_type_by_label(self, label):
		"""Get room type row by reference or label"""
		for rt in self.room_types:
			if rt.room_type_ref == label or str(rt.idx) == label:
				return rt
		return None

	def create_rate_record(self, period, room_type, tariff, hotel_doc, occupancy_class, base_cost,
							is_supplement=False, supplement_name=None):
		"""Create a single MN Rate record"""
		net_price = base_cost
		margin_pct = self.margin_pct_default or 0
		gross_price = net_price * (1 + margin_pct / 100.0)

		min_los = period.min_length_of_stay_override or self.min_length_of_stay_global or 1

		rate = frappe.get_doc({
			"doctype": "MN Rate",
			"service_type": "hotel",
			"service_ref": self.hotel,
			"room_type_ref": room_type.room_type_ref,
			"region_district": hotel_doc.region_district or "",
			"city": hotel_doc.city or "",
			"date_from": period.date_from,
			"date_to": period.date_to,
			"board": tariff.board,
			"occupancy_class": occupancy_class,
			"uom": tariff.uom or self.rate_basis_uom,
			"per": tariff.per or self.rate_basis_period,
			"is_supplement": 1 if is_supplement else 0,
			"supplement_name": supplement_name,
			"rate_type": "Net",
			"channel": "B2B-NET",
			"base_cost": base_cost,
			"net_price": net_price,
			"gross_price": gross_price,
			"margin_pct": margin_pct,
			"release_days": period.release_days or 0,
			"min_length_of_stay": min_los,
			"stop_sale": period.stop_sale or 0,
			"priority": period.priority or 10,
			"source": "contract",
			"source_contract": self.name,
			"effective_from": self.effective_from,
			"effective_to": self.effective_to
		})
		return rate

	def generate_occupancy_rates(self, period, room_type, tariff, hotel_doc, base_cost):
		"""Generate rates for different occupancy scenarios"""
		count = 0

		for occ_rule in self.occupancy_rules:
			# Check if rule applies to this room type
			if occ_rule.applies_to:
				applies_to_list = [x.strip() for x in occ_rule.applies_to.split(",")]
				if room_type.room_type_ref not in applies_to_list:
					continue

			# Calculate price based on rule
			if occ_rule.is_free:
				occ_price = 0
			elif occ_rule.charge_type == "Fixed Amount":
				occ_price = occ_rule.value
			else:  # Percent of Base
				occ_price = base_cost * (occ_rule.value / 100.0)

			rate = self.create_rate_record(
				period=period,
				room_type=room_type,
				tariff=tariff,
				hotel_doc=hotel_doc,
				occupancy_class=occ_rule.target,
				base_cost=occ_price
			)
			rate.insert(ignore_permissions=True)
			count += 1

		return count

	def generate_supplement_rates(self, supplement):
		"""Generate rates for supplements"""
		count = 0
		hotel_doc = frappe.get_doc("Hotel", self.hotel)

		# Get applicable periods
		applicable_periods = []
		if supplement.applies_to_periods:
			period_labels = [x.strip() for x in supplement.applies_to_periods.split(",")]
			for period in self.periods:
				if period.label in period_labels:
					applicable_periods.append(period)
		else:
			applicable_periods = self.periods

		for period in applicable_periods:
			for room_type in self.room_types:
				# Create supplement rate
				rate = frappe.get_doc({
					"doctype": "MN Rate",
					"service_type": "hotel",
					"service_ref": self.hotel,
					"room_type_ref": room_type.room_type_ref,
					"region_district": hotel_doc.region_district or "",
					"city": hotel_doc.city or "",
					"date_from": period.date_from,
					"date_to": period.date_to,
					"board": supplement.name1,  # Supplement acts as board upgrade
					"occupancy_class": "Supplement",
					"uom": supplement.per_scope,
					"per": "Per Day",
					"is_supplement": 1,
					"supplement_name": supplement.name1,
					"rate_type": "Net",
					"channel": "B2B-NET",
					"base_cost": supplement.amount,
					"net_price": supplement.amount,
					"gross_price": supplement.amount * 1.15,  # Default margin
					"margin_pct": 15,
					"release_days": period.release_days or 0,
					"min_length_of_stay": 1,
					"stop_sale": period.stop_sale or 0,
					"priority": period.priority or 10,
					"source": "contract",
					"source_contract": self.name,
					"effective_from": self.effective_from,
					"effective_to": self.effective_to
				})
				rate.insert(ignore_permissions=True)
				count += 1

		return count


@frappe.whitelist()
def contract_to_rates(contract_name):
	"""
	API method to compile contract into rates.
	Usage: frappe.call('mn_hotel_rates.mn_hotel_rates.doctype.mn_contract.mn_contract.contract_to_rates',
	                    contract_name='CONTRACT-001')
	"""
	contract = frappe.get_doc("MN Contract", contract_name)
	return contract.generate_rates()
