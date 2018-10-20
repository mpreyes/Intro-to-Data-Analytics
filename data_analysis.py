from datetime import datetime as dt
import unicodecsv
from collections import defaultdict
import numpy as np

import matplotlib.pyplot as plt


def read_csv(filename):
    with open(filename,'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)


def parse_date(date):
	if date == '':
		return None
	else:
		return dt.strptime(date, '%Y-%m-%d')
 

def parse_maybe_int(i):
	if i == '':
		return None
	else:
		return int(i)
     
        
def get_unique_students(data):
	unique_students = set()
	for data_pt in data:
		unique_students.add(data_pt['account_key'])
	return unique_students

def remove_udacity_account(data, udacity_test_accounts):
	non_udacity_data = []
	for data_pt in data:
		if data_pt['account_key'] not in udacity_test_accounts:
			non_udacity_data.append(data_pt)
	return non_udacity_data

def within_one_week(join_date, engagement_date):
	time_delta = engagement_date - join_date
	return time_delta.days < 7 and time_delta.days >= 0

def remove_free_trial_cancels(data, paid_students):
	new_data = []
	for data_pt in data:
		if data_pt['account_key'] in paid_students:
			new_data.append(data_pt)
	return new_data


def group_data(data,key_name):
	grouped_data = defaultdict(list)
	for data_pt in data:
		key = data_pt[key_name]
		grouped_data[key].append(data_pt)
	return grouped_data

def sum_grouped_items(grouped_data, field_name):
	summed_data = {}
	for key, data_pts in grouped_data.items():
		total = 0 
		for data_pt in data_pts:
			total += data_pt[field_name]
		summed_data[key] = total
	return summed_data




def describe_data(data, data_name):

	print(str(data_name) + " stats")
	print("mean: " + str(np.mean(data)))
	print("std dev: " + str(np.std(data)))
	print("min: " + str(np.min(data)))
	print("max: " + str(np.max(data)))
	print("\n")
	plt.hist(data,bins=8)
	plt.xlabel(data_name)
	plt.show()



def main():
	enrollments = read_csv("Enrollments.csv")
	daily_engagement = read_csv("Daily_engagement.csv")
	#daily_engagement_full = read_csv("Daily_engagement_full.csv")
	project_submissions = read_csv("Project_submissions.csv")
	

#enrollments data cleanup
	enrollment_num_rows = 0
	engagement_num_rows = 0
	submission_num_rows = 0  

	unique_enrollments_students = get_unique_students(enrollments)
	unique_engagements_students = get_unique_students(daily_engagement)
	unique_submissions_students = get_unique_students(project_submissions)

	for enrollment in enrollments:
		enrollment_num_rows += 1
		enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
		enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
		enrollment['is_canceled'] = enrollment['is_canceled'] == "True"
		enrollment['is_udacity'] = enrollment['is_udacity'] == "True"
		enrollment['join_date'] = parse_date(enrollment['join_date'])

#engagements data cleanup
	for engagement_record in daily_engagement:
		engagement_num_rows += 1
		engagement_record['lessons_completed'] = int(float(engagement_record['lessons_completed']))
		engagement_record['num_courses_visited'] = int(float(engagement_record['num_courses_visited']))
		engagement_record['projects_completed'] = int(float(engagement_record['projects_completed']))
		engagement_record['total_minutes_visited'] = float(engagement_record['total_minutes_visited'])
		engagement_record['utc_date'] = parse_date(engagement_record['utc_date'])

#submissions table cleanup
	for submission in project_submissions:
		submission_num_rows += 1

		submission['completion_date'] = parse_date(submission['completion_date'])
		submission['creation_date'] = parse_date(submission['creation_date'])

	#enrollments[0]
	#print(daily_engagement[0]['account_key'])
	#print(unique_enrollments_students)

	udacity_test_accounts = set()
	for enrollment in enrollments:
		if enrollment['is_udacity']:
			udacity_test_accounts.add(enrollment['account_key'])


	


	non_udacity_enrollments = remove_udacity_account(enrollments,udacity_test_accounts)
	non_udacity_engagements = remove_udacity_account(daily_engagement,udacity_test_accounts)
	non_udacity_submissions = remove_udacity_account(project_submissions,udacity_test_accounts)


	paid_students = {}
	for enrollment in non_udacity_enrollments:
		if enrollment['days_to_cancel'] == None or enrollment['days_to_cancel'] > 7:
			if enrollment['account_key'] not in paid_students or enrollment['join_date'] > paid_students[enrollment['account_key']]:
				paid_students[enrollment['account_key']] = enrollment['join_date']
		


	paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments,paid_students)
	paid_engagement =  remove_free_trial_cancels(non_udacity_engagements,paid_students)
	paid_submissions = remove_free_trial_cancels(non_udacity_submissions,paid_students)

	for engagement_record in paid_engagement:
		if engagement_record['num_courses_visited'] > 0:
			engagement_record['has_visited'] = 1
		else:
			engagement_record['has_visited'] = 0

	paid_engagement_in_first_week = []
	
	for engagement_record in paid_engagement:
		account_key = engagement_record['account_key']
		join_date = paid_students[account_key]
		engagement_record_date = engagement_record['utc_date'] 
		if within_one_week(join_date,engagement_record_date):
			paid_engagement_in_first_week.append(engagement_record)


	print(len(paid_engagement_in_first_week))

	# engagement_by_account = defaultdict(list)
	# for engagement_record in paid_engagement_in_first_week:
	# 	account_key = engagement_record['account_key']
	# 	engagement_by_account[account_key].append(engagement_record)
	
	engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')


	total_minutes_by_account = sum_grouped_items(engagement_by_account, 'total_minutes_visited')
	total_lesssons_by_account = sum_grouped_items(engagement_by_account, 'lessons_completed')
	total_visits_by_account = sum_grouped_items(engagement_by_account, 'has_visited')

	# for account_key, engagement_for_student in engagement_by_account.items():
	# 	total_minutes = 0
	# 	num_lessons = 0
	# 	num_courses_visited = 0
	# 	for engagement_record in engagement_for_student:
	# 		num_lessons += engagement_record['lessons_completed']
	# 		total_minutes += engagement_record['total_minutes_visited']
	# 		num_courses_visited += engagement_record['has_visited']
	# 	total_minutes_by_account[account_key] = total_minutes
	# 	total_lesssons_by_account[account_key] = num_lessons
	# 	total_visits_by_account[account_key] = num_courses_visited
	
	
	total_minutes = total_minutes_by_account.values()
	total_lessons = total_lesssons_by_account.values()
	total_visited = total_visits_by_account.values()
	#describe_data(total_minutes, "total minutes")
	#describe_data(total_lessons, "total lessons")
	#describe_data(total_visited, "total courses visited")


	subway_project_lesson_keys = [ '746169184','3176718735']

	pass_subway_project = set()
	passing_engagement = []
	non_passing_engagement = []

	for submission in paid_submissions:
		if submission['lesson_key'] in subway_project_lesson_keys:
			if submission['assigned_rating'] == 'PASSED' or submission['assigned_rating'] == 'DISTINCTION':
			 	pass_subway_project.add(submission['account_key'])
	

	for engagment_record in paid_engagement_in_first_week:
		if engagment_record['account_key'] in pass_subway_project:
			passing_engagement.append(engagement_record['account_key'])
		else:
			non_passing_engagement.append(engagement_record['account_key'])
		

	days_to_complete = 0
	num_students = 0
	for submission in paid_submissions:
		creation_date =  submission['creation_date']
		completion_date =  submission['completion_date']
		if submission['assigned_rating'] == 'PASSED' or submission['assigned_rating'] == 'DISTINCTION':
			if completion_date != None and creation_date != None:
				dif = aacompletion_date - creation_date
				days_to_complete += dif.days
				num_students += 1
			else:
				dif = -1
			if dif != -1:
				print creation_date, completion_date, dif.days
	
	print days_to_complete, num_students
	print days_to_complete // num_students












main()
