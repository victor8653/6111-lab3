# CS6111 Project 3: Association Rule Mining with A-Priori

**Team Members:**
- Piers Ozuah (UNI: pjo2123)  
- Victor Xie (UNI: yx2801)

## 📦 Files Submitted

- `main.py`  
- `INTEGRATED-DATASET.csv`  
- `output.txt` (as `example-run.txt`)  
- `README.pdf` 

The VM is set up exactly following the instructions in the assignment specification.

## How to Set Up and Run This Project
This project is designed to run on a Google Cloud VM configured for 6111 project 3.


### VM Software Installation
```bash
sudo apt-get -y update
sudo apt-get install -y python3 python3-pip python3-venv git python3-testresources
pip3 install --upgrade google-api-python-client
```


### Python Virtual Environment Setup
```bash
python3 -m venv dbproj
source dbproj/bin/activate
pip install pandas numpy
```

### How to Run the Program

Run the project with the following command:

```bash
python3 main.py INTEGRATED-DATASET.csv 0.1 0.7
```





## Dataset Description

### a) 
We used the NYC Parks Special Events dataset, found here: https://data.cityofnewyork.us/Recreation/Parks-Special-Events/6v4b-5gp4/about_data .

### b) 
- We first filtered the parks special events to only include events under the fitness category and sports category. We then filtered the data to exclude rows that did not have information in the audience column.

- We then process the data with the following steps:
If the event name is not available we replace it with “unknown_name”

- We then bucketize the attendance where less than or equal to 5 people is low attendance, less than or equal to 75 people is medium attendance, and otherwise it is large attendance. We set these numbers for the buckets after viewing the rows of our data and recognizing the common ranges of attendances. 

- These values are then added to a column labeled “attendance_bucket”

- We then create columns for the different types of audiences and flag them as True if they are present in the original audience list. 

- We then get the time of day of each event where 5AM to 12PM is morning time, 12PM to 5PM is afternoon time, and 5PM to 5AM is evening time, and add these to a time_of_day column.

Next, we use the day of each event to state whether an event was during a weekday or weekend and add this information to our day_type column.

### c) 
We found this dataset compelling because it leads to insights about the timing, location, audiences, and attendance for special fitness and sport events held throughout the city. We felt it would be interesting to see the patterns underlying when these events are planned, who the target audiences are, and how popular the events are among the public. Furthermore, the dataset is compelling because we were able to compare the special park events held between the five different boroughs. 


## Algorithm Design

Our implementation is based on the A-Priori algorithm as described in the Agrawal and Srikant (1994) paper. We used Python dictionaries and sets to optimize support counting and candidate generation, avoiding hash trees but implementing all required A-Priori pruning techniques.

No external libraries beyond `pandas`, `csv`, and `itertools` were used for algorithm logic.



## Internal Design (How Our Code Works)
Our project follows the standard A-Priori algorithm, like the one in the Agrawal and Srikant paper. We didn’t use hash tree, but we wrote everything from scratch and made sure it works for our dataset.

The basic idea is:
we read the data (each row becomes a transaction),
then find itemsets that appear frequently enough (based on the support threshold),
and then we look for rules where “if A happens, B usually also happens” (using confidence threshold).

Here’s how we organized the code:

Data Loading:
We load the CSV file and treat each row as a set of items. To make items unique and easier to understand, we combined column names and values, like "Category_Fitness" instead of just "Fitness". This helps avoid confusion when different columns have the same values (like “weekend” showing up in two places).

A-Priori Algorithm:
We count single items first, and then build larger itemsets level by level. For example, from frequent 1-itemsets we generate 2-item candidates, then 3-item candidates, and so on. We only keep the ones that appear often enough. When generating candidates, we check that all subsets are also frequent — that’s the classic A-Priori trick to cut down on useless combinations.

Rule Generation:
For each frequent itemset, we try breaking it up into a rule like A => B. If the confidence is high enough, we keep that rule. We only allow one item on the right-hand side of the rule, which was required in the project spec.

Output:
We write everything to output.txt. First we show all the frequent itemsets with their support, and then the rules with their confidence and support. Everything is sorted so it's easier to read.

We didn’t really change the algorithm much, but we did slightly customize how we format items, just to make things easier to read and analyze.

### Sample Run Command:

```bash
python3 main.py INTEGRATED-DATASET.csv 0.1 0.7
```

​    Some of the association rules that were revealing include the following:
['Category_Fitness', 'day_type_weekday'] => ['time_of_day_afternoon_time'] 
(Conf: 85.0%, Supp: 21.4728%)
This rule was surprising because it indicates that fitness events in parks on weekdays are likely to happen in the afternoon, when many people may be at work or in school.

​    ['Borough_Bronx'] => ['day_type_weekday'] (Conf: 86.3%, Supp: 26.6861%)
This rule suggests that most of the special events held in the Bronx occur during weekdays, which is surprising because we expected most events to be held on weekends when people may have more free time.

['Event Type_Community Based Event', 'children_audience_True'] =>
['day_type_weekday'] (Conf: 86.3%, Supp: 27.2330%)
This rule suggesting that most community based events that target children are likely to be held on weekdays is interesting because event organizers seem to hold the events during weekdays to give children an activity to do while their parents may be at work, rather than holding the events on weekends for children and their parents to participate together.