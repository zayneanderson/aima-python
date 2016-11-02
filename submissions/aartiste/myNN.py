from sklearn import datasets
from sklearn.neural_network import MLPClassifier
import traceback
from submissions.aartiste import election
from submissions.aartiste import county_demographics

class DataFrame:
    data = []
    feature_names = []
    target = []
    target_names = []

trumpECHP = DataFrame()

'''
Extract data from the CORGIS elections, and merge it with the
CORGIS demographics.  Both data sets are organized by county and state.
'''
joint = {}

elections = election.get_results()
for county in elections:
    try:
        st = county['Location']['State Abbreviation']
        countyST = county['Location']['County'] + st
        trump = county['Vote Data']['Donald Trump']['Percent of Votes']
        joint[countyST] = {}
        joint[countyST]['ST']= st
        joint[countyST]['Trump'] = trump
    except:
        traceback.print_exc()

demographics = county_demographics.get_all_counties()
for county in demographics:
    try:
        countyNames = county['County'].split()
        cName = ' '.join(countyNames[:-1])
        st = county['State']
        countyST = cName + st
        # elderly =
        # college =
        # home =
        # poverty =
        if countyST in joint:
            joint[countyST]['Elderly'] = county['Age']["Percent 65 and Older"]
            joint[countyST]['HighSchool'] = county['Education']["Bachelor's Degree or Higher"]
            joint[countyST]['College'] = county['Education']["Bachelor's Degree or Higher"]
            joint[countyST]['Home'] = county['Housing']["Homeownership Rate"]
            joint[countyST]['Poverty'] = county['Income']["Persons Below Poverty Level"]
    except:
        traceback.print_exc()

'''
Remove the counties that did not appear in both samples.
'''
intersection = {}
for countyST in joint:
    if 'College' in joint[countyST]:
        intersection[countyST] = joint[countyST]

trumpECHP.data = []

'''
Build the input frame, row by row.
'''
for countyST in intersection:
    # choose the input values
    trumpECHP.data.append([
        # countyST,
        # intersection[countyST]['ST'],
        # intersection[countyST]['Trump'],
        intersection[countyST]['Elderly'],
        intersection[countyST]['College'],
        intersection[countyST]['Home'],
        intersection[countyST]['Poverty'],
    ])

trumpECHP.feature_names = [
    # 'countyST',
    # 'ST',
    # 'Trump',
    'Elderly',
    'College',
    'Home',
    'Poverty',
]

'''
Build the target list,
one entry for each row in the input frame.

The Naive Bayesian network is a classifier,
i.e. it sorts data points into bins.
The best it can do to estimate a continuous variable
is to break the domain into segments, and predict
the segment into which the variable's value will fall.
In this example, I'm breaking Trump's % into two
arbitrary segments.
'''
trumpECHP.target = []

def trumpTarget(percentage):
    if percentage > 45:
        return 1
    return 0

for countyST in intersection:
    # choose the target
    tt = trumpTarget(intersection[countyST]['Trump'])
    trumpECHP.target.append(tt)

trumpECHP.target_names = [
    'Trump <= 45%',
    'Trump >  45%',
]

mlpc = MLPClassifier(
    solver='sgd',
    learning_rate = 'adaptive',
)

Examples = {
    'TrumpDefault': {
        'frame': trumpECHP,
    },
    'TrumpSGD': {
        'frame': trumpECHP,
        'mlpc': mlpc
    },
}