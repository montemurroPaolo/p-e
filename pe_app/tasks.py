from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from .models import *
from .utils import *

if test:
    the_time = 1
else:
    the_time = 5

@periodic_task(crontab(minute=f'*/{the_time}'))
def every_one_mins():

    defillama = Get_defillama()
    defillama = Defillama_df_from_dict(defillama)

    coingecko = Coingecko_data()

    merged = Merge_and_clean(defillama,coingecko)

    Create_csv(merged)
    Create_csv_hour()