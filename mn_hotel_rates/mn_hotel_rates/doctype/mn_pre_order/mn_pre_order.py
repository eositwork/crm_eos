# -*- coding: utf-8 -*-
# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class MNPreOrder(Document):
	def validate(self):
		"""Validate pre-order"""
		# Calculate warning datetime
		if self.release_datetime and self.warning_hours_before:
			release_dt = frappe.utils.get_datetime(self.release_datetime)
			self.warning_datetime = frappe.utils.add_to_date(
				release_dt, hours=-self.warning_hours_before)

		# Calculate nights if not set
		if self.date_from and self.date_to and not self.nights:
			from_date = frappe.utils.getdate(self.date_from)
			to_date = frappe.utils.getdate(self.date_to)
			self.nights = (to_date - from_date).days

		# Set agent if not set
		if not self.agent:
			self.agent = frappe.session.user

	@frappe.whitelist()
	def confirm_order(self):
		"""Confirm the pre-order and convert to Sales Order"""
		if self.status != "Pending":
			frappe.throw(_("Only pending pre-orders can be confirmed"))

		now = frappe.utils.now_datetime()
		release_dt = frappe.utils.get_datetime(self.release_datetime)

		if now > release_dt:
			frappe.throw(_("Cannot confirm - release time has passed"))

		self.status = "Confirmed"
		self.confirmed_at = frappe.utils.now()
		self.confirmed_by = frappe.session.user
		self.save()

		# Optionally create Sales Order
		# sales_order = self.create_sales_order()
		# return sales_order.name

		frappe.msgprint(_("Pre-order confirmed successfully"))
		return self.name

	@frappe.whitelist()
	def cancel_order(self, reason="Manual Cancellation"):
		"""Cancel the pre-order"""
		if self.status == "Confirmed":
			frappe.throw(_("Cannot cancel confirmed order"))

		self.status = "Cancelled"
		self.cancelled_at = frappe.utils.now()
		self.cancelled_by = frappe.session.user
		self.cancellation_reason = reason
		self.save()

		frappe.msgprint(_("Pre-order cancelled"))
		return self.name

	def send_warning_notification(self):
		"""Send warning notification before release"""
		if self.warning_sent:
			return

		# Get notification template
		try:
			notification = frappe.get_doc("Email Template", "Pre Order Warning")
			subject = notification.subject
			message = frappe.render_template(notification.response, {"doc": self})
		except:
			subject = _("Pre-Order Release Warning: {0}").format(self.name)
			message = _("""
				<p>Dear {0},</p>
				<p>This is a reminder that your pre-order <strong>{1}</strong> will be released in {2} hours.</p>
				<p><strong>Booking Details:</strong></p>
				<ul>
					<li>Hotel: {3}</li>
					<li>Board: {4}</li>
					<li>Check-in: {5}</li>
					<li>Check-out: {6}</li>
					<li>Total Price: {7} {8}</li>
				</ul>
				<p>Please confirm your order before <strong>{9}</strong> to avoid cancellation.</p>
				<p>Thank you!</p>
			""").format(
				self.agent,
				self.name,
				self.warning_hours_before,
				self.hotel,
				self.board,
				self.date_from,
				self.date_to,
				self.total_price,
				self.currency,
				frappe.utils.format_datetime(self.release_datetime)
			)

		# Send email to agent
		if self.agent:
			frappe.sendmail(
				recipients=[self.agent],
				subject=subject,
				message=message,
				reference_doctype=self.doctype,
				reference_name=self.name
			)

		self.warning_sent = 1
		self.warning_sent_at = frappe.utils.now()
		self.save(ignore_permissions=True)

	def send_release_notification(self):
		"""Send notification when order is released/expired"""
		if self.release_notification_sent:
			return

		# Get notification template
		try:
			notification = frappe.get_doc("Email Template", "Pre Order Released")
			subject = notification.subject
			message = frappe.render_template(notification.response, {"doc": self})
		except:
			subject = _("Pre-Order Expired: {0}").format(self.name)
			message = _("""
				<p>Dear {0},</p>
				<p>Your pre-order <strong>{1}</strong> has been automatically cancelled due to release time expiration.</p>
				<p><strong>Booking Details:</strong></p>
				<ul>
					<li>Hotel: {2}</li>
					<li>Board: {3}</li>
					<li>Check-in: {4}</li>
					<li>Check-out: {5}</li>
					<li>Total Price: {6} {7}</li>
				</ul>
				<p>Please create a new booking if you still wish to proceed.</p>
				<p>Thank you!</p>
			""").format(
				self.agent,
				self.name,
				self.hotel,
				self.board,
				self.date_from,
				self.date_to,
				self.total_price,
				self.currency
			)

		# Send email to agent
		if self.agent:
			frappe.sendmail(
				recipients=[self.agent],
				subject=subject,
				message=message,
				reference_doctype=self.doctype,
				reference_name=self.name
			)

		self.release_notification_sent = 1
		self.release_notification_sent_at = frappe.utils.now()
		self.save(ignore_permissions=True)

	def create_sales_order(self):
		"""Create Sales Order from confirmed pre-order"""
		if self.status != "Confirmed":
			frappe.throw(_("Only confirmed pre-orders can be converted to Sales Order"))

		# Create Sales Order
		so = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": self.customer,
			"transaction_date": frappe.utils.today(),
			"delivery_date": self.date_from,
			"items": [{
				"item_code": "Hotel Booking",  # Should exist as an Item
				"item_name": "{0} - {1}".format(self.hotel, self.board),
				"description": "Hotel: {0}\nRoom: {1}\nBoard: {2}\nCheck-in: {3}\nCheck-out: {4}\nNights: {5}\nPax: {6}+{7}".format(
					self.hotel, self.room_type or "Standard", self.board,
					self.date_from, self.date_to, self.nights,
					self.adults, self.children
				),
				"qty": self.nights,
				"rate": self.hotel_price / self.nights if self.nights else self.hotel_price,
				"amount": self.hotel_price,
				# MN custom fields
				"mn_service_type": "hotel",
				"mn_service_ref": self.hotel,
				"mn_room_type": self.room_type,
				"mn_board": self.board,
				"mn_date_from": self.date_from,
				"mn_date_to": self.date_to,
				"mn_nights": self.nights,
				"mn_pax": self.adults + self.children
			}]
		})

		# Add transfer if exists
		if self.transfer_price > 0:
			so.append("items", {
				"item_code": "Transfer",  # Should exist as an Item
				"item_name": "Airport Transfer",
				"qty": 1,
				"rate": self.transfer_price,
				"amount": self.transfer_price,
				"mn_service_type": "transfer"
			})

		# Add additional services if exists
		if self.additional_services_price > 0:
			so.append("items", {
				"item_code": "Additional Services",
				"item_name": "Additional Services",
				"qty": 1,
				"rate": self.additional_services_price,
				"amount": self.additional_services_price
			})

		so.insert()

		# Link SO to pre-order
		self.db_set("sales_order", so.name)

		return so


@frappe.whitelist()
def check_pre_order_releases():
	"""
	Scheduled task to check pre-orders for warnings and releases.
	Called every hour via scheduler.
	"""
	now = frappe.utils.now_datetime()

	# Find pending pre-orders
	pre_orders = frappe.get_all("MN Pre Order",
		filters={"status": "Pending"},
		fields=["name", "warning_datetime", "release_datetime", "warning_sent", "release_notification_sent"]
	)

	warnings_sent = 0
	orders_released = 0

	for po_dict in pre_orders:
		po = frappe.get_doc("MN Pre Order", po_dict.name)

		# Check if warning should be sent
		if not po.warning_sent and po.warning_datetime:
			warning_dt = frappe.utils.get_datetime(po.warning_datetime)
			if now >= warning_dt:
				try:
					po.send_warning_notification()
					warnings_sent += 1
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Pre Order Warning Failed: " + po.name)

		# Check if release time has passed
		if po.release_datetime:
			release_dt = frappe.utils.get_datetime(po.release_datetime)
			if now >= release_dt:
				try:
					po.status = "Expired"
					po.cancelled_at = frappe.utils.now()
					po.cancellation_reason = "Release Expired"
					po.save(ignore_permissions=True)
					po.send_release_notification()
					orders_released += 1
				except Exception as e:
					frappe.log_error(frappe.get_traceback(), "Pre Order Release Failed: " + po.name)

	frappe.db.commit()

	return {
		"warnings_sent": warnings_sent,
		"orders_released": orders_released
	}
