import nltk
import random
import requests
import pandas as pd

from unicodedata import normalize
from sqlalchemy import create_engine
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'dmlops',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 26),
    'email': ['dmlops@dmlops.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def string_normalize(data):
    result = normalize('NFKD', data) \
        .encode('ASCII', 'ignore')

    return result.decode('ASCII')


def gender_features(word):
    try:
        return {'last_letter': word[-1]}

    except Exception as exception:
        print(exception)


"""
RAW LAYER
"""


def data_provider(data='https://raw.githubusercontent.com/biaacarvalhoo27/dataops/main/data/names.csv',
                  eng=create_engine('mysql+pymysql://dmlops:dmlops@mysql:3306/dmlops', pool_recycle=3600)):
    cnx = eng.connect()

    df = pd.read_csv(data, sep=';')

    try:
        df.to_sql('raw', cnx, if_exists='replace', index=False)

        return

    except Exception as exception:
        return exception


"""
CLEANED LAYER
"""


def data_cleansing(table='cleaned',
                   eng=create_engine('mysql+pymysql://dmlops:dmlops@mysql:3306/dmlops', pool_recycle=3600)):
    cnx = eng.connect()

    df = pd.DataFrame()

    try:
        df = pd.read_sql('select * from dmlops.raw', cnx)

    except Exception as exception:
        print(exception)

    df['name'] = df['name'].apply(lambda x: string_normalize(x).upper())

    try:
        df.to_sql(table, cnx, if_exists='replace', index=False)

        return

    except Exception as exception:
        return exception


"""
CURATED LAYER
"""


def data_loader(table='curated',
                eng=create_engine('mysql+pymysql://dmlops:dmlops@mysql:3306/dmlops', pool_recycle=3600)):
    cnx = eng.connect()

    df = pd.DataFrame()

    try:
        df = pd.read_sql('select * from dmlops.cleaned', cnx)

    except Exception as exception:
        print(exception)

    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %HH:%MM:%SS')

    try:
        df.to_sql(table, cnx, if_exists='replace', index=False)

        return

    except Exception as exception:
        return exception


"""
ANALYTICS LAYER
"""


def data_analytics(table='analytics',
                   eng=create_engine('mysql+pymysql://dmlops:dmlops@mysql:3306/dmlops', pool_recycle=3600)):
    url = 'https://raw.githubusercontent.com/biaacarvalhoo27/dataops/main/data'

    male = requests.get('{}/male.txt'.format(url)).text
    female = requests.get('{}/female.txt'.format(url)).text

    male_list = [line.lower() for line in male.split('\n') if len(line) > 0]
    female_list = [line.lower() for line in female.split('\n') if len(line) > 0]

    labeled_names = ([(name, 'male') for name in male_list] +
                     [(name, 'female') for name in female_list])

    random.shuffle(labeled_names)

    feature_sets = [(gender_features(name), gender) for name, gender in labeled_names]

    train_set, test_set = feature_sets[900:], feature_sets[:900]

    classifier = nltk.NaiveBayesClassifier.train(train_set)

    print(classifier.labels())

    print(nltk.classify.accuracy(classifier, train_set))

    print(classifier.show_most_informative_features())

    cnx = eng.connect()

    df = pd.DataFrame()

    try:
        df = pd.read_sql('select * from dmlops.curated', cnx)

    except Exception as exception:
        print(exception)

    df['gender'] = df['name'].apply(lambda x: classifier.classify(gender_features(x.lower())).upper())

    try:
        df.to_sql(table, cnx, if_exists='replace', index=False)

        return

    except Exception as exception:
        return exception


dag = DAG('dmlops_workflow',
          start_date=datetime(2023, 10, 1),
          schedule_interval='@daily',
          catchup=False)

data_provider = PythonOperator(
    task_id='data_provider',
    python_callable=data_provider,
    dag=dag
)

data_cleansing = PythonOperator(
    task_id='data_cleansing',
    python_callable=data_cleansing,
    dag=dag
)

data_loader = PythonOperator(
    task_id='data_loader',
    python_callable=data_loader,
    dag=dag
)

data_analytics = PythonOperator(
    task_id='data_analytics',
    python_callable=data_analytics,
    dag=dag
)

workflow = [data_provider >> data_cleansing >> data_loader >> data_analytics]
