import requests
import signal
import time
import json
import pandas as pd

#Returns all lender_ids for all loans of a certain loan 'status' which can be funded, fundraising, paid, etc.
#need to add proxies to avoid getting temporarily blocked.
def get_lender_ids(status):
    all_lenders = []
    ss = requests.session()
    loans_with_monies = ss.get('http://api.kivaws.org/v1/loans/search.json?status=' + status)
    time.sleep(1)
    loans_with_monies = loans_with_monies.content.decode('utf-8')
    jason = json.loads(loans_with_monies)
    pages = int(jason['paging']['pages'])
    loan_ids = []
    for i in range(1,pages+1):
        loans_with_monies = ss.get('http://api.kivaws.org/v1/loans/search.json?status=' + status + '&' + 'page=' + str(i))
        time.sleep(1.1)
        loans_with_monies = loans_with_monies.content.decode('utf-8')
        jason = json.loads(loans_with_monies)
        print 'Page: '+str(i)
        for loan in jason['loans']:
            loan_ids.append(loan['id'])
        # if i == 10:
        #     break
    lender_ids = []
    print "COMPLETE: COLLECTING LOAN IDS"
    for loanID in loan_ids:
        lenders_for_loan = ss.get('http://api.kivaws.org/v1/loans/' + str(loanID) + '/lenders.json')
        time.sleep(1.1)
        lenders_for_loan = lenders_for_loan.content.decode('utf-8')
        jason = json.loads(lenders_for_loan)
        for lender in jason['lenders']:
            if (lender['name'] == 'Anonymous'):
                continue
            lender_ids.append(lender['lender_id'])
    return lender_ids

def get_lender_info(lender_list):
    lender_reasons = {}
    lender_occupation = {}
    for username in lender_list:
        lender_data = ss.get('http://api.kivaws.org/v1/lenders/' + str(username) + '.json')
        time.sleep(1.1)
        lenders_for_loan = lender_data.content.decode('utf-8')
        jason = json.loads(lender_data)
        lender_reasons[str(username)] = jason['lenders'][0]['loan_because']
        lender_occupation[str(username)] = jason['lenders'][0]['occupational_info']
    return lender_reasons, lender_occupation




if __name__ == "__main__":
    lender_ids_funded = get_lender_ids('funded')
    lender_ids_paid = get_lender_ids('paid')
    lender_ids_in_repayment = get_lender_ids('in_repayment')
    lender_reason, lender_occupation = get_lender_info(lender_ids_funded)
    lender_reason_2, lender_occupation_2 = get_lender_info(lender_ids_paid)
    lender_reason_3, lender_occupation_3 = get_lender_info(lender_ids_in_repayment)

    lender_reason.update(lender_reason_2)
    lender_reason.update(lender_reason_3)
    lender_occupation.update(lender_occupation_2)
    lender_occupation.update(lender_occupation_3)

    print("Completed getting data")
    file1 = open('lender_reasons.json', 'w')
    file1.write(str(lender_reason))
    file1.close()
    file2 = open('lender_occupation.json', 'w')
    file2.write(str(lender_occupation))
    file2.close()
