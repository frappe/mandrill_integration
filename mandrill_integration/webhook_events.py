# Copyright (c) 2015, Frappe Technologies Pvt. Ltd.
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import hmac
import hashlib
import json
from .webhooks import get_webhook_post_url

@frappe.whitelist(allow_guest=True)
def notify(mandrill_events=None):
	"""Mandrill Webhook will call this public method. the authenticate_signature method will verify the signature.

		mandrill_events = [
			{
				"_id": "d4df1868bc1a44148f134f43f5e53380",
				"event": "send",
				"msg": {
					"_id": "d4df1868bc1a44148f134f43f5e53380",
					"clicks": [],
					"email": "recipient@example.com",
					"metadata": {
						"message_id": "<COMM-00005@localhost>"
					},
					"opens": [],
					"reject": null,
					"resends": [],
					"sender": "sender@example.com",
					"smtp_events": [],
					"state": "sent",
					"subaccount": null,
					"subject": "Test Subject",
					"tags": [],
					"template": null,
					"ts": 1438067635
				},
				"ts": 1438067635
			}
		]
	"""
	if not authenticate_signature():
		# print "not authenticated"
		return

	# print frappe.as_json(json.loads(mandrill_events), indent=2)

	mandrill_events = json.loads(mandrill_events) or []
	for event in mandrill_events:
		set_status(event)

def set_status(event):
	"""Find the communication using message id and set delivery status if the recipient matches"""
	msg = event.get("msg", {})

	communication = get_communication(msg)

	if communication:
		recipient = msg.get("email")

		# delivery status should be set as per the original recipient of the communication
		if recipient in communication.recipients:
			set_delivery_status(communication, msg, event)

def get_communication(msg):
	"""Extracts message id from metadata and return communication doc"""
	message_id = msg.get("metadata", {}).get("message_id") or ""
	if message_id and "@{site}".format(site=frappe.local.site) in message_id:
		communication_name = message_id.strip(" <>").split("@", 1)[0]
		return frappe.get_doc("Communication", communication_name)
	else:
		return None

event_state_map = {
	"sent": "Sent",
	"rejected": "Rejected",
	"spam": "Marked As Spam",
	"unsub": "Recipient Unsubscribed",
	"bounced": "Bounced",
	"soft-bounced": "Soft-Bounced",
	"clicks": "Clicked",
	"opens": "Opened"
}

def set_delivery_status(communication, msg, event):
	"""Evaluate event type, message state, clicks and opens and set the delivery status of the communication"""

	event_type = event.get("event")
	state = msg.get("state")

	if event_type in ("spam", "unsub"):
		delivery_status = event_state_map.get(event_type)

	elif state == "sent":
		if len(msg.get("clicks")) > 0:
			delivery_status = event_state_map["clicks"]

		elif len(msg.get("opens")) > 0:
			delivery_status = event_state_map["opens"]

		else:
			delivery_status = event_state_map["sent"]

	else:
		delivery_status = event_state_map.get(state)

	if delivery_status:
		# print "Delivery Status of {0} is {1}".format(communication.name, delivery_status)
		communication.db_set("delivery_status", delivery_status)

def authenticate_signature():
	"""Returns True if the received signature matches the generated signature"""
	received_signature = frappe.get_request_header("X-Mandrill-Signature")

	# seems like a dummy post request
	if not received_signature:
		return False

	to_hash = get_post_url_for_hashing()
	for key in get_webhook_keys():
		# generate signature using the webhook key
		hashed = hmac.new(key.encode("utf-8"), to_hash, hashlib.sha1)
		generated_signature = hashed.digest().encode("base64").rstrip('\n')

		# matched => authenticated
		if received_signature==generated_signature:
			return True

	# no match => failure
	return False

def get_post_url_for_hashing():
	"""Concats site's post url for set_status, and sorted key and value of request parameters"""
	post_url = get_webhook_post_url()
	post_args = ""

	for key in sorted(frappe.local.form_dict.keys()):
		if key != "cmd":
			post_args += key + frappe.local.form_dict[key]

	return post_url + post_args

def get_webhook_keys():
	"""There could be multiple email accouts with Mandrill Integration"""
	def _get_webhook_keys():
		return [d.mandrill_webhook_key for d in frappe.get_all("Email Account",
			fields=["mandrill_webhook_key"],
			filters={
				"enable_outgoing": 1,
				"service": "Mandrill"
			}) if d.mandrill_webhook_key]

	return frappe.cache().get_value("mandrill_webhook_keys", _get_webhook_keys)
