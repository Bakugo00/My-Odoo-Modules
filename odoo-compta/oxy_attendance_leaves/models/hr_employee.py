# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from pytz import utc
from datetime import timedelta
from collections import defaultdict
from odoo.tools import float_utils
from odoo.addons.resource.models.resource_mixin import timezone_datetime

ROUNDING_FACTOR = 16

class hr_employee(models.Model):
	_inherit = "hr.employee"

	def get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None, include_dayoff=False):
		"""
			By default the resource calendar is used, but it can be
			changed using the `calendar` argument.

			`domain` is used in order to recognise the leaves to take,
			None means default value ('time_type', '=', 'leave')

			Returns a dict {'days': n, 'hours': h} containing the
			quantity of working time expressed as days and as hours.
		"""
		resource = self.resource_id
		calendar = calendar or self.resource_calendar_id

		# naive datetimes are made explicit in UTC
		if not from_datetime.tzinfo:
			from_datetime = from_datetime.replace(tzinfo=utc)
		if not to_datetime.tzinfo:
			to_datetime = to_datetime.replace(tzinfo=utc)

		# total hours per day: retrieve attendances with one extra day margin,
		# in order to compute the total hours on the first and last days
		from_full = from_datetime - timedelta(days=1)
		to_full = to_datetime + timedelta(days=1)
		intervals = calendar._attendance_intervals(from_full, to_full, resource, include_dayoff=include_dayoff)
		day_total = defaultdict(float)
		for start, stop, meta in intervals:
			day_total[start.date()] += (stop - start).total_seconds() / 3600

		# actual hours per day
		if compute_leaves:
			intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain, include_dayoff=include_dayoff)
		else:
			intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource, include_dayoff=include_dayoff)
		day_hours = defaultdict(float)
		for start, stop, meta in intervals:
			day_hours[start.date()] += (stop - start).total_seconds() / 3600

		# compute number of days as quarters
		days = sum(
			float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
			for day in day_hours
		)
		
		return {
			'days': days,
			'hours': sum(day_hours.values()),
		}

	def _get_work_days_data_batch(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None, include_dayoff=False):
		"""
			By default the resource calendar is used, but it can be
			changed using the `calendar` argument.

			`domain` is used in order to recognise the leaves to take,
			None means default value ('time_type', '=', 'leave')

			Returns a dict {'days': n, 'hours': h} containing the
			quantity of working time expressed as days and as hours.
		"""
		#raise Exception(include_dayoff)
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
			day_total = calendar._get_resources_day_total(from_datetime, to_datetime, calendar_resources, include_dayoff=include_dayoff)
			# actual hours per day
			if compute_leaves:
				intervals = calendar._work_intervals_batch(from_datetime, to_datetime, calendar_resources, domain, include_dayoff=include_dayoff)
			else:
				intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, calendar_resources, include_dayoff=include_dayoff)
			
			for calendar_resource in calendar_resources:
				result[calendar_resource.id] = calendar._get_days_data(intervals[calendar_resource.id], day_total[calendar_resource.id])

		# convert "resource: result" into "employee: result"
		return {mapped_employees[r.id]: result[r.id] for r in resources}