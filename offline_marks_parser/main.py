from requests_html import HTML, HTMLSession
import sys
import json
import argparse

cmd_args = str(sys.argv)

# Command line arguments.
response_url = None
answer_key_url = None
file_name = None
cmd_parser = argparse.ArgumentParser(
    description="Parses candidate's response sheet, calculates marks, and stores results as JSON.")
cmd_parser.add_argument(
    '-r', '--response', help="Candidate's response key URL.", dest='response_url')
cmd_parser.add_argument(
    '-k', '--key', help="Answer key URL.", dest='answer_key_url')
cmd_parser.add_argument('-o', '--output', help="Print output to file.", dest='file_name')
args = cmd_parser.parse_args()

response_url = args.response_url
answer_key_url = args.answer_key_url
file_name = args.file_name

if(response_url == None):
    response_url = input('Enter Response Sheet URL: ')
if(answer_key_url == None):
    answer_key_url = input('Enter Answer Key URL: ')

# Function to set marks to the items (needs refactoring, maybe later!!)
def getMarksFromData(parsed_data_list):
    one_mark=1.0
    two_mark=2.0
    c_one_mark=1.0
    i_one_mark=-1.0 * (1.0 / 3.0)
    c_two_mark=2.0
    i_two_mark=-1.0 * (2.0 / 3.0)
    zero_mark=0

    for item in parsed_data_list:
        if item['response_given'] != "--":
            if item['question_type'] == "MCQ":
                if item['response_given'] == item['actual_answer']:
                    item['marks_obtained'] = c_one_mark if item['question_mark'] == one_mark else c_two_mark
                else:
                    item['marks_obtained'] = i_one_mark if item['question_mark'] == one_mark else i_two_mark
            
            elif item['question_type'] == "MSQ":
                expected_list = item['actual_answer'].split(";")
                actual_list = item['response_given'].split(",")

                if sorted(expected_list) == actual_list:
                    item['marks_obtained'] = c_one_mark if item['question_mark'] == one_mark else c_two_mark
                else:
                    item['marks_obtained'] = i_one_mark if item['question_mark'] == one_mark else i_two_mark

            elif item['question_type'] == "NAT":
                if item['actual_answer'].find(':') != -1:
                    expected_range = item['actual_answer'].split(":")
                    fresponse_given = float(item['response_given'])
                    if fresponse_given >= float(expected_range[0]) and fresponse_given <= float(expected_range[1]):
                        item['marks_obtained'] = c_one_mark if item['question_mark'] == one_mark else c_two_mark
                    else:
                        item['marks_obtained'] = i_one_mark if item['question_mark'] == one_mark else i_two_mark
                else:
                    expected_answer = item['actual_answer']
                    response_given = item['response_given']
                    if expected_answer == response_given:
                        item['marks_obtained'] = c_one_mark if item['question_mark'] == one_mark else c_two_mark
                    else:
                        item['marks_obtained'] = i_one_mark if item['question_mark'] == one_mark else i_two_mark
        else:
            item['marks_obtained'] = zero_mark
    
    return parsed_data_list


# with open('go.html') as html_file:
#     source = html_file.read()
#     html = HTML(html=source)

# Creating session to parse the data
session = HTMLSession()

try:
    r = session.get(response_url)
    if r.status_code != 200:
        print("Getting this error: ", r.status_code)
        sys.exit(-1)
except:
    print("Could not load GATE response sheet! Exiting..")
    sys.exit(-1)

html = r.html

try:
    r2 = session.get(answer_key_url)   
    if r.status_code != 200:
        print("Getting this error: ", r.status_code)
        sys.exit(-1)
except:
    print("Could not load GO answer sheet! Exiting..")
    sys.exit(-1)

# html2 = r2.html.render()
html2 = r2.html

# Used Variables
question_answer_dict = dict()
question_subject_dict = dict()
parsed_data_list = list()
apt_code="g"
cs_code="c"
one_mark=1.0
two_mark=2.0

# Parsing the GO answer key spreadsheet (this depends on the sheet formatting)
whole_table = html2.find('table.waffle', first = True)

all_data = whole_table.find('td')
# question_and_answer = whole_table.find('td.s0')
# subject_id = whole_table.find('td.s2')

for i in range(3, len(all_data), 4):
    question_answer_dict[all_data[i-3].text.rstrip()] = all_data[i-2].text.rstrip().replace('"', '')
    question_subject_dict[all_data[i-3].text.rstrip()] = all_data[i].text.rstrip()

# print(question_answer_dict, question_subject_dict)


# Parsing GATE Response sheet
match = html.find('div.section-cntnr')

for i in match:
    section_name = i.find('div.section-lbl', first=True).find('span.bold', first=True).text
    questions = i.find('div.question-pnl')

    for j in questions:
        parsed_subdata = dict()
        question_number_list = j.find('table.questionRowTbl', first=True).find('img')
        question_image_name = str(question_number_list[0].attrs['name'])

        last_question_number = question_image_name.split(".")[0].split("q")[-1]
        # print(last_question_number)

        if section_name.rstrip() == "General Aptitude":
            final_question_number = apt_code + last_question_number
        else:
            final_question_number = cs_code + last_question_number

        if final_question_number.find(apt_code) != -1:
            if int(last_question_number) <= 5:
                parsed_subdata['question_mark'] = one_mark
            else:
                parsed_subdata['question_mark'] = two_mark
        else:
            if int(last_question_number) <= 25:
                parsed_subdata['question_mark'] = one_mark
            else:
                parsed_subdata['question_mark'] = two_mark

        parsed_subdata['question_short_id'] = final_question_number

        question_menu_table = j.find('table.menu-tbl', first=True).find('td.bold')
        # for labels in question_menu_table:
            # print(labels.text)

        parsed_subdata['question_type'] = question_menu_table[0].text.rstrip()
        parsed_subdata['question_long_id'] = question_menu_table[1].text.rstrip()
        
        # print(question_menu_table[2].text)
        if question_menu_table[2].text.rstrip() == "Not Answered" or question_menu_table[2].text.rstrip().find("Not") != -1:
            parsed_subdata['response_given'] = "--"
        else:
            if parsed_subdata['question_type'] == "NAT":
                nat_answer = j.find('table.questionRowTbl', first=True).find('td.bold')[-1].text
                parsed_subdata['response_given'] = nat_answer.rstrip()
            else:
                option_code = list()
                mapped_option_code = list()
                for i in range(1, len(question_number_list)):
                    option_code.append(str(question_number_list[i].attrs['name']).rstrip().split(".")[0].split(last_question_number)[-1].upper())
                # print(parsed_subdata['question_type'], option_code, parsed_subdata['question_long_id'])

                given_response_sheet = question_menu_table[3].text.rstrip().split(",")

                for i in given_response_sheet:
                    mapped_option_code.append(option_code[int(i) - 1])

                compress_mapped_option = ",".join(mapped_option_code)
                # print(compress_mapped_option)
                parsed_subdata['response_given'] = compress_mapped_option

            # if(labels.text == "NAT"):
            #     ques_type = j.find('table.questionRowTbl', first=True).find('td.bold')[-1].text
            #     print(ques_type)

        parsed_subdata['actual_answer'] = question_answer_dict[final_question_number]
        parsed_subdata['subject_id'] = question_subject_dict[final_question_number]

        parsed_data_list.append(parsed_subdata)

# print(parsed_data_list)

final_data = getMarksFromData(parsed_data_list)

# Writing to the required json
if file_name == None:
    json_final_data = json.dumps(final_data, indent=4)
    print(json_final_data)
else:
# If write to a file
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

print("\n\nJSON data created. Exiting!")

