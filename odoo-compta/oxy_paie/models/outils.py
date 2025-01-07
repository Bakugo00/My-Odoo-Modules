# -*- coding: utf-8 -*-
from datetime import datetime, time

def nb_jour_mois(date_from,date_to):
	return (date_to-date_from).days + 1

def calcul_iep(marge,qty,exper,sal_base):
	r = float(qty)
	res = (exper/marge) * sal_base * (r/100) 
	return res

def prime_prorata(prime,abss):
	return prime - (prime/173.33 * abss)

def prime_taux(prime,base):
	return (base * prime) / 100

def irg10(payslip):
	tmp = ""
	for rule in payslip.struct_id.rule_ids:
		if rule.irg_10:
			tmp += str(rule.code) + '+'
	return tmp[:-1]

def truncate(n, decimals=2):
	multiplier = 10.0 ** decimals
	return int(n * multiplier) / multiplier

def get_prime_asiduite(worked_days,amount):
	asid = amount
	for wdays in worked_days:
		if wdays.code != 'WORK100':
			if (wdays.code == 'R068' and (wdays.number_of_hours / 60) >= 15) or (wdays.code != 'R068' and wdays.code != 'R073' and (wdays.number_of_hours * 60) >= 15) or (wdays.code == 'R073' and wdays.number_of_hours > 8):
				asid = 0
				break
			elif (wdays.code == 'R073' and wdays.number_of_hours <=8 and wdays.number_of_hours > 0):
				asid = amount/8 * (8 - wdays.number_of_hours)
	return asid

def get_prime_rendement(accident_travail,type_prime_rendement,absences,amount):
	if type_prime_rendement == 'fixe' and (absences - accident_travail) < 16 :
		if (absences - accident_travail) > 0:
			return amount/173.33 * (173.33 - (absences - accident_travail))
		else:
			return amount
	elif type_prime_rendement == 'init':
		return amount
	return 0

def get_nb_mois_travailler(contract,date_from,date_to):
	if contract.date_start > date_from:
		suppose_day_from = datetime.combine(date_from,time(0,0,0))
		day_to = datetime.combine(date_to,time(0,0,0))
		suppose_work_data = contract.employee_id.get_work_days_data(suppose_day_from, day_to, calendar=contract.resource_calendar_id)
		day_from = datetime.combine(contract.date_start,time(0,0,0))
		work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
		return contract.nb_heure_mois_moyen - (suppose_work_data['hours'] - work_data['hours'])