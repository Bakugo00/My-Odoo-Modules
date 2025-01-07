# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.addons.resource.models.resource_mixin import timezone_datetime
from collections import defaultdict

class resource_mixin(models.AbstractModel):
	_inherit = "resource.mixin"

	def _get_work_days_data_batch(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None, include_dayoff=False):
		"""
			By default the resource calendar is used, but it can be
			changed using the `calendar` argument.

			`domain` is used in order to recognise the leaves to take,
			None means default value ('time_type', '=', 'leave')

			Returns a dict {'days': n, 'hours': h} containing the
			quantity of working time expressed as days and as hours.
		"""
		resources = self.mapped('resource_id')
		mapped_employees = {e.resource_id.id: e.id for e in self}
		result = {}

		# naive datetimes are made explicit in UTC
		from_datetime = timezone_datetime(from_datetime)
		to_datetime = timezone_datetime(to_datetime)

		mapped_resources = defaultdict(lambda: self.env['resource.resource'])
		for record in self:
			mapped_resources[calendar or record.resource_calendar_id] |= record.resource_id

		for calendar, calendar_resources in mapped_resources.items():
			day_total = calendar._get_resources_day_total(from_datetime, to_datetime, calendar_resources)
			# actual hours per day
			if compute_leaves:
				intervals = calendar._work_intervals_batch(from_datetime, to_datetime, calendar_resources, domain, include_dayoff)
			else:
				intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, calendar_resources, include_dayoff)
			
			for calendar_resource in calendar_resources:
				result[calendar_resource.id] = calendar._get_days_data(intervals[calendar_resource.id], day_total[calendar_resource.id])

		# convert "resource: result" into "employee: result"
		return {mapped_employees[r.id]: result[r.id] for r in resources} 