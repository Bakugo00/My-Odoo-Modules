# -*- coding: utf-8 -*-from odoo import models
from odoo import models
import xlrd
from datetime import date, datetime
import time
from odoo.tools import ustr
import calendar

class BisXlsx(models.AbstractModel):
	_name="report.oxy_paie.bis_xlsx"
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, obj):
		year = data['year']
		sheet_bis = workbook.add_worksheet('301 Bis')
		format_bold = workbook.add_format({'font_size': 12, 'align': 'vcenter' ,'bold': True,})
		heading_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True , 'size':12})
		format_title = workbook.add_format({'font_size': 12, 'align': 'left' ,'bold': True,})
		format_title2 = workbook.add_format({'font_size': 9, 'align': 'left', 'valign' : 'top' ,'bold': False,})
		format_title3 = workbook.add_format({'font_size': 9, 'align': 'vcenter', 'valign' : 'center',})
		format_amount = workbook.add_format({'font_size': 9, 'align': 'right', 'valign' : 'top', 'num_format' : '# ##0.00'})
		format_center_total = workbook.add_format({'font_size': 10, 'align': 'right','bold': True, 'border' : 1, 'num_format': '# ##0.00'})
		format_total_title = workbook.add_format({'font_size': 10, 'align': 'vcenter','valign' : 'center', 'bold': True, 'border' : 1})
		sheet_bis.set_column('A:A', 3)
		sheet_bis.set_column('B:B', 15)
		sheet_bis.set_column('C:C', 7)
		sheet_bis.set_column('P:P', 10)
		sheet_bis.set_column('L:L', 11)
		sheet_bis.set_column('N:N', 11)
		sheet_bis.set_column('O:O', 10)
		format_title.set_border(2)
		format_title2.set_border(2)
		format_title3.set_border(1)
		format_amount.set_border(1)
		sheet_bis.write('A2,A2', self.env.user.company_id.name, heading_format)
		street = self.env.user.company_id.street and self.env.user.company_id.street or ''
		street2 = self.env.user.company_id.street2 and self.env.user.company_id.street2 or ''
		city = self.env.user.company_id.city and self.env.user.company_id.city or ''
		sheet_bis.merge_range('A3:C3', street + ' ' + street2 + ' ' + city, heading_format)
		sheet_bis.merge_range('M3:O3', 'Edition du ' + time.strftime('%d/%m/%Y'), heading_format)
		sheet_bis.merge_range('G5:L5', 'DECLARATION ANNUELLE DES IRG SUR SALAIRES ' + year, heading_format)
		sheet_bis.write('D7,D7', 'Janvier', format_title)
		sheet_bis.write('E7,E7', ustr('Février'), format_title)
		sheet_bis.write('F7,F7', 'Mars', format_title)
		sheet_bis.write('G7,G7', 'Avril', format_title)
		sheet_bis.write('H7,H7', 'Mai', format_title)
		sheet_bis.write('I7,I7', 'Juin', format_title)
		sheet_bis.write('J7,J7', 'Juillet', format_title)
		sheet_bis.write('K7,K7', ustr('Août'), format_title)
		sheet_bis.write('L7,L7', 'Septembre', format_title)
		sheet_bis.write('M7,M7', 'Octobre', format_title)
		sheet_bis.write('N7,O7', 'Novembre', format_title)
		sheet_bis.write('O7,O7', ustr('Décembre'), format_title)
		format_title2.set_text_wrap()
		format_title3.set_text_wrap()
		sheet_bis.write('A8,A8', 'NO', format_title2)
		sheet_bis.write('B8,B8', ustr('NOM & PRENOM'), format_title2)
		sheet_bis.write('C8,C8', ustr('SIT/FAM\nN/ENF'), format_title2)
		sheet_bis.write('D8,D8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('E8,E8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('F8,F8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('G8,G8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('H8,H8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('I8,I8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('J8,J8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('K8,K8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('L8,L8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('M8,M8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('N8,N8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('O8,O8', ustr('SAL.IMP.\nRet.IRG'), format_title2)
		sheet_bis.write('P8,P8', ustr('SAL.IMP.10%\nRet.10%'), format_title2)
		sheet_bis.write('Q8,Q8', ustr('Tot.IMP.\nTot.IRG'), format_title2)

		year_prec = int(year)
		month_prec = 1
		month = 1
		day_start = self.env.user.company_id.day_start and self.env.user.company_id.day_start or str(1)
		day_end = self.env.user.company_id.day_end
		day_decembre = day_end and day_end or str(31)
		if int(day_start) != 1:
			year_prec -= 1
			month_prec = 12
		date_start = datetime.strptime(str(year_prec)+'-'+str(month_prec)+'-'+day_start,'%Y-%m-%d').date()
		date_end = datetime.strptime(str(year)+'-'+str(12)+'-'+day_decembre,'%Y-%m-%d').date()
		payslip_lines = self.env['hr.payslip.line'].search([('slip_id.state','=','done'),('slip_id.date_from','>=',date_start),('slip_id.date_to','<=',date_end)])
		emp_ids = []
		for line in payslip_lines:
			if line.slip_id.employee_id.id not in emp_ids:
				emp_ids.append(line.slip_id.employee_id.id)
		janvier_debut = date_start
		janv_day_end = day_end
		if not janv_day_end:
			janv_day_end = calendar.monthrange(int(year),1)[1]
		janvier_fin = datetime.strptime(str(year)+'-'+str(month)+'-'+str(janv_day_end),'%Y-%m-%d').date()

		fevrier_debut, fevrier_fin = self.get_month(day_start, day_end, 2, year)
		mars_debut, mars_fin = self.get_month(day_start, day_end, 3, year)
		avril_debut, avril_fin = self.get_month(day_start, day_end, 4, year)
		mai_debut, mai_fin = self.get_month(day_start, day_end, 5, year)
		juin_debut, juin_fin = self.get_month(day_start, day_end, 6, year)
		juillet_debut, juillet_fin = self.get_month(day_start, day_end, 7, year)
		aout_debut, aout_fin = self.get_month(day_start, day_end, 8, year)
		sept_debut, sept_fin = self.get_month(day_start, day_end, 9, year)
		oct_debut, oct_fin = self.get_month(day_start, day_end, 10, year)
		nov_debut, nov_fin = self.get_month(day_start, day_end, 11, year)
		dec_debut, dec_fin = self.get_month(day_start, day_end, 12, year)
		res = {}
		for emp in emp_ids:
			janvier_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',janvier_debut),('slip_id.date_to','<=',janvier_fin)])
			sal_imp = 0
			irg = 0
			irg10 = 0
			irg10_base = 0
			res.update({emp : {}})
			for line in janvier_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount
				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'01' : [sal_imp,irg]})

			fevrier_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',fevrier_debut),('slip_id.date_to','<=',fevrier_fin)])
			sal_imp = 0
			irg = 0
			for line in fevrier_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount
				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'02' : [sal_imp,irg]})

			mars_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',mars_debut),('slip_id.date_to','<=',mars_fin)])
			sal_imp = 0
			irg = 0
			for line in mars_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount
				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'03' : [sal_imp,irg]})

			avril_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',avril_debut),('slip_id.date_to','<=',avril_fin)])
			sal_imp = 0
			irg = 0
			for line in avril_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'04' : [sal_imp,irg]})

			mai_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',mai_debut),('slip_id.date_to','<=',mai_fin)])
			sal_imp = 0
			irg = 0
			for line in mai_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 = line.total
						irg10_base -= line.amount

			res[emp].update({'05' : [sal_imp,irg]})

			juin_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',juin_debut),('slip_id.date_to','<=',juin_fin)])
			sal_imp = 0
			irg = 0
			for line in juin_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'06' : [sal_imp,irg]})

			juillet_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',juillet_debut),('slip_id.date_to','<=',juillet_fin)])
			sal_imp = 0
			irg = 0
			for line in juillet_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'07' : [sal_imp,irg]})

			aout_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',aout_debut),('slip_id.date_to','<=',aout_fin)])
			sal_imp = 0
			irg = 0
			for line in aout_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'08' : [sal_imp,irg]})

			sept_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',sept_debut),('slip_id.date_to','<=',sept_fin)])
			sal_imp = 0
			irg = 0
			for line in sept_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'09' : [sal_imp,irg]})

			oct_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',oct_debut),('slip_id.date_to','<=',oct_fin)])
			sal_imp = 0
			irg = 0
			for line in oct_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'10' : [sal_imp,irg]})

			nov_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',nov_debut),('slip_id.date_to','<=',nov_fin)])
			sal_imp = 0
			irg = 0
			for line in nov_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'11' : [sal_imp,irg]})

			dec_lines = self.env['hr.payslip.line'].search([('employee_id','=',emp),('slip_id.state','=','done'),('slip_id.date_from','>=',dec_debut),('slip_id.date_to','<=',dec_fin)])
			sal_imp = 0
			irg = 0
			for line in dec_lines:
				if not line.slip_id.credit_note:
					if line.code == 'SIMP':
						sal_imp += line.total
					elif line.code == 'R660':
						irg += line.total
					elif line.code == 'R663':
						irg10 += line.total
						irg10_base += line.amount

				else:
					if line.code == 'SIMP':
						sal_imp -= line.total
					elif line.code == 'R660':
						irg -= line.total
					elif line.code == 'R663':
						irg10 -= line.total
						irg10_base -= line.amount

			res[emp].update({'12' : [sal_imp,irg]})
			res[emp].update({'irg10' : [irg10_base,irg10]})

		line = 9
		i = 1
		for r in res:
			emp_obj = self.env['hr.employee'].browse(r)
			marital = ''
			nb_enfant = emp_obj.children
			if emp_obj.marital == 'single':
				marital = 'C'
			elif emp_obj.marital == 'married':
				marital = 'M'
			elif emp_obj.marital == 'widower':
				marital = 'V'
			elif emp_obj.marital == 'divorced':
				marital = 'D'

			prenom = emp_obj.prenom and emp_obj.prenom or ''
			sheet_bis.merge_range('A%s:A%s'%(line,line+1), i, format_title3)
			sheet_bis.merge_range('B%s:B%s'%(line,line+1), emp_obj.complete_name, format_title3)
			sheet_bis.merge_range('C%s:C%s'%(line,line+1), marital + '\n' + str(nb_enfant), format_title3)
			sheet_bis.write('D%s,D%s'%(line,line), res[r]['01'][0], format_amount)
			sheet_bis.write('D%s,D%s'%(line+1,line+1), res[r]['01'][1], format_amount)
			sheet_bis.write('E%s,E%s'%(line,line), res[r]['02'][0], format_amount)
			sheet_bis.write('E%s,E%s'%(line+1,line+1), res[r]['02'][1], format_amount)
			sheet_bis.write('F%s,F%s'%(line,line), res[r]['03'][0], format_amount)
			sheet_bis.write('F%s,F%s'%(line+1,line+1), res[r]['03'][1], format_amount)
			sheet_bis.write('G%s,G%s'%(line,line), res[r]['04'][0], format_amount)
			sheet_bis.write('G%s,G%s'%(line+1,line+1), res[r]['04'][1], format_amount)
			sheet_bis.write('H%s,H%s'%(line,line), res[r]['05'][0], format_amount)
			sheet_bis.write('H%s,H%s'%(line+1,line+1), res[r]['05'][1], format_amount)
			sheet_bis.write('I%s,I%s'%(line,line), res[r]['06'][0], format_amount)
			sheet_bis.write('I%s,I%s'%(line+1,line+1), res[r]['06'][1], format_amount)
			sheet_bis.write('J%s,J%s'%(line,line), res[r]['07'][0], format_amount)
			sheet_bis.write('J%s,J%s'%(line+1,line+1), res[r]['07'][1], format_amount)
			sheet_bis.write('K%s,K%s'%(line,line), res[r]['08'][0], format_amount)
			sheet_bis.write('K%s,K%s'%(line+1,line+1), res[r]['08'][1], format_amount)
			sheet_bis.write('L%s,L%s'%(line,line), res[r]['09'][0], format_amount)
			sheet_bis.write('L%s,L%s'%(line+1,line+1), res[r]['09'][1], format_amount)
			sheet_bis.write('M%s,M%s'%(line,line), res[r]['10'][0], format_amount)
			sheet_bis.write('M%s,M%s'%(line+1,line+1), res[r]['10'][1], format_amount)
			sheet_bis.write('N%s,N%s'%(line,line), res[r]['11'][0], format_amount)
			sheet_bis.write('N%s,N%s'%(line+1,line+1), res[r]['11'][1], format_amount)
			sheet_bis.write('O%s,O%s'%(line,line), res[r]['12'][0], format_amount)
			sheet_bis.write('O%s,O%s'%(line+1,line+1), res[r]['12'][1], format_amount)
			sheet_bis.write('P%s,P%s'%(line,line), res[r]['irg10'][0], format_amount)
			sheet_bis.write('P%s,P%s'%(line+1,line+1), res[r]['irg10'][1], format_amount)

			sheet_bis.write_formula('Q%s,Q%s' % (line,line),'{=SUM(D%s:P%s)}' % (line, line), format_center_total)
			sheet_bis.write_formula('Q%s,Q%s' % (line+1,line+1),'{=SUM(D%s:P%s)}' % (line+1, line+1), format_center_total)
			line += 2
			i += 1
		sheet_bis.merge_range('A%s:C%s'%(line,line+1), 'TOTAL GENERAL', format_total_title)
		column = 'D'
		while (column != 'R'):
			formula_d_p = self.get_formula(column, line, False)
			sheet_bis.write('%s%s,%s%s'%(column,line,column,line), '{=%s}' % ustr(formula_d_p[:-1]), format_center_total)
			formula_d_u = self.get_formula(column, line, True)
			sheet_bis.write('%s%s,%s%s'%(column,line+1,column,line+1), '{=%s}' % ustr(formula_d_u[:-1]), format_center_total)
			column = chr(ord(column) + 1)

	def get_month(self, day_start, day_end, month, year):
		month_tmp = month
		if day_start != '1':
			month_tmp = month - 1
		date_debut = datetime.strptime(str(year)+'-'+str(month_tmp)+'-'+day_start,'%Y-%m-%d').date()
		day_tmp_end = day_end
		if not day_tmp_end:
			day_tmp_end = calendar.monthrange(int(year),int(month))[1]
		date_fin = datetime.strptime(str(year)+'-'+str(month)+'-'+str(day_tmp_end),'%Y-%m-%d').date()
		return date_debut, date_fin

	def get_formula(self, column, number, pair):
		tmp = ''
		for i in range(9,number):
			if pair:
				if i % 2 == 0:
					tmp += column+str(i)+'+'
			else:
				if i % 2 != 0:
					tmp += column+str(i)+'+'
		return tmp