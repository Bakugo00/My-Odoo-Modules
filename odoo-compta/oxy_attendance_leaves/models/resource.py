# -*- coding: utf-8 -*-

from collections import defaultdict
import math
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY
from functools import partial
from itertools import chain
from pytz import timezone, utc

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_round

from odoo.tools import date_utils, float_utils
from odoo.addons.resource.models.resource import Intervals, float_to_time


class ResourceCalendar(models.Model):
	_inherit = "resource.calendar"

	def _attendance_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None, include_dayoff=False):
		""" Return the attendance intervals in the given datetime range.
			The returned intervals are expressed in specified tz or in the resource's timezone.
		"""
		self.ensure_one()
		resources = self.env['resource.resource'] if not resources else resources
		assert start_dt.tzinfo and end_dt.tzinfo
		combine = datetime.combine

		resources_list = list(resources) + [self.env['resource.resource']]
		resource_ids = [r.id for r in resources_list]
		domain = domain if domain is not None else []
		domain = expression.AND([domain, [
			('calendar_id', '=', self.id),
			('resource_id', 'in', resource_ids),
			('display_type', '=', False),
		]])

		# for each attendance spec, generate the intervals in the date range
		cache_dates = defaultdict(dict)
		cache_deltas = defaultdict(dict)
		result = defaultdict(list)
		if not include_dayoff:
			for attendance in self.env['resource.calendar.attendance'].search(domain):
				for resource in resources_list:
					# express all dates and times in specified tz or in the resource's timezone
					tz = tz if tz else timezone((resource or self).tz)
					if (tz, start_dt) in cache_dates:
						start = cache_dates[(tz, start_dt)]
					else:
						start = start_dt.astimezone(tz)
						cache_dates[(tz, start_dt)] = start
					if (tz, end_dt) in cache_dates:
						end = cache_dates[(tz, end_dt)]
					else:
						end = end_dt.astimezone(tz)
						cache_dates[(tz, end_dt)] = end

					start = start.date()
					if attendance.date_from:
						start = max(start, attendance.date_from)
					until = end.date()
					if attendance.date_to:
						until = min(until, attendance.date_to)
					if attendance.week_type:
						start_week_type = int(math.floor((start.toordinal()-1)/7) % 2)
						if start_week_type != int(attendance.week_type):
							# start must be the week of the attendance
							# if it's not the case, we must remove one week
							start = start + relativedelta(weeks=-1)
					weekday = int(attendance.dayofweek)

					if self.two_weeks_calendar and attendance.week_type:
						days = rrule(WEEKLY, start, interval=2, until=until, byweekday=weekday)
					else:
						days = rrule(DAILY, start, until=until, byweekday=weekday)

					for day in days:
						# attendance hours are interpreted in the resource's timezone
						hour_from = attendance.hour_from
						if (tz, day, hour_from) in cache_deltas:
							dt0 = cache_deltas[(tz, day, hour_from)]
						else:
							dt0 = tz.localize(combine(day, float_to_time(hour_from)))
							cache_deltas[(tz, day, hour_from)] = dt0

						hour_to = attendance.hour_to
						if (tz, day, hour_to) in cache_deltas:
							dt1 = cache_deltas[(tz, day, hour_to)]
						else:
							dt1 = tz.localize(combine(day, float_to_time(hour_to)))
							cache_deltas[(tz, day, hour_to)] = dt1
						result[resource.id].append((max(cache_dates[(tz, start_dt)], dt0), min(cache_dates[(tz, end_dt)], dt1), attendance))
		else:
			att = self.env['resource.calendar.attendance'].search(domain)
			for attendance in range(0, 7):
				for resource in resources_list:
					# express all dates and times in specified tz or in the resource's timezone
					tz = tz if tz else timezone((resource or self).tz)
					if (tz, start_dt) in cache_dates:
						start = cache_dates[(tz, start_dt)]
					else:
						start = start_dt.astimezone(tz)
						cache_dates[(tz, start_dt)] = start
					if (tz, end_dt) in cache_dates:
						end = cache_dates[(tz, end_dt)]
					else:
						end = end_dt.astimezone(tz)
						cache_dates[(tz, end_dt)] = end
					start = start.date()
					until = end.date()
					if att:
						if att[0].date_from:
							start = max(start, att[0].date_from)
						if att[0].date_to:
							until = min(until, att[0].date_to)

					if self.two_weeks_calendar:
						days = rrule(WEEKLY, start, interval=2, until=until)
					else:
						days = rrule(DAILY, start, until=until)
					for day in days:
						# attendance hours are interpreted in the resource's timezone
						hour_from = att[0].hour_from
						if (tz, day, hour_from) in cache_deltas:
							dt0 = cache_deltas[(tz, day, hour_from)]
						else:
							dt0 = tz.localize(combine(day, float_to_time(hour_from)))
							cache_deltas[(tz, day, hour_from)] = dt0

						hour_to = att[0].hour_to
						if (tz, day, hour_to) in cache_deltas:
							dt1 = cache_deltas[(tz, day, hour_to)]
						else:
							dt1 = tz.localize(combine(day, float_to_time(hour_to)))
							cache_deltas[(tz, day, hour_to)] = dt1
						result[resource.id].append((max(cache_dates[(tz, start_dt)], dt0), min(cache_dates[(tz, end_dt)], dt1), att[0]))
		return {r.id: Intervals(result[r.id]) for r in resources_list}


	def _work_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None, include_dayoff=False):
		""" Return the effective work intervals between the given datetimes. """
		if not resources:
			resources = self.env['resource.resource']
			resources_list = [resources]
		else:
			resources_list = list(resources)

		attendance_intervals = self._attendance_intervals_batch(start_dt, end_dt, resources, tz=tz, include_dayoff=include_dayoff)
		leave_intervals = self._leave_intervals_batch(start_dt, end_dt, resources, domain, tz=tz)
		return {
			r.id: (attendance_intervals[r.id] - leave_intervals[r.id]) for r in resources_list
		}

	def _get_resources_day_total(self, from_datetime, to_datetime, resources=None, include_dayoff=False):
		"""
		@return dict with hours of attendance in each day between `from_datetime` and `to_datetime`
		"""
		self.ensure_one()
		resources = self.env['resource.resource'] if not resources else resources
		resources_list = list(resources) + [self.env['resource.resource']]
		# total hours per day:  retrieve attendances with one extra day margin,
		# in order to compute the total hours on the first and last days
		from_full = from_datetime - timedelta(days=1)
		to_full = to_datetime + timedelta(days=1)
		intervals = self._attendance_intervals_batch(from_full, to_full, resources=resources, include_dayoff=include_dayoff)

		result = defaultdict(lambda: defaultdict(float))
		for resource in resources_list:
			day_total = result[resource.id]
			for start, stop, meta in intervals[resource.id]:
				day_total[start.date()] += (stop - start).total_seconds() / 3600
		return result