from .utils import *
from django.shortcuts import render

def home(request):
    csv_file_hour_path = "{}/pe_data_hour.csv".format(settings.BASE_DIR)
    
    merged = pd.read_csv(csv_file_hour_path)

    plot_pe = Plot_pe(merged).to_html()

    context = {
        "plot_pe":plot_pe
    }

    return render(request, 'home.html', context)