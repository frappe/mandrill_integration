from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "mandrill-integration",
					"label": "Mandrill Integration",
					"description": _("How to integrate email status with Mandrill"),
				},
			]
		}
	]
