# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import datetime, time

class hr_leave(models.Model):
	_inherit = "hr.leave"


	@api.onchange('date_from', 'date_to', 'employee_id', 'holiday_status_id', 'holiday_status_id.include_dayoff')
	def _onchange_leave_dates(self):
		if self.date_from and self.date_to:
			self.number_of_days = self._get_number_of_days(date_from=self.date_from, date_to=self.date_to, employee_id=self.employee_id.id, include_dayoff=self.holiday_status_id.include_dayoff)['days']
		else:
			self.number_of_days = 0

	def _get_number_of_days(self, date_from, date_to, employee_id, include_dayoff=False):
		""" Returns a float equals to the timedelta between two dates given as string."""
		if employee_id:
			employee = self.env['hr.employee'].browse(employee_id)
			return employee._get_work_days_data_batch(date_from, date_to, include_dayoff=include_dayoff)[employee.id]

		today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
			datetime.combine(date_from.date(), time.min),
			datetime.combine(date_from.date(), time.max),
			False)

		hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)

		return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}