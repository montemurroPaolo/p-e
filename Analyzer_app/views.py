from .utils import *

def home(request):

    # Get the files
    name_sheets_comm = ["Anagrafiche", "Trattative", "CRMCommerciale"]
    comm_sheets = OpenSpreadSheet('CrM Commerciale 2023 - The ', name_sheets_comm)

    name_sheets_track = ["CTS", "bar", "estratto", "corsi", "private", "spese", "spese_straordinarie"]
    track_sheets = OpenSpreadSheet('Tracking', name_sheets_track)

    name_sheets_staff = ["staff"]
    staff_sheets = OpenSpreadSheet('Staff the gym', name_sheets_staff)

    # Clean the files
    anagrafiche = comm_sheets[0]
    trattative = clean_trattative(comm_sheets[1])  # not so good
    commerciale = clean_commerciale(comm_sheets[2])
    cts = track_sheets[0]
    bar = track_sheets[1]
    estratto = track_sheets[2]
    corsi = clean_corsi(track_sheets[3])
    private = clean_private(track_sheets[4])
    spese = clean_spese(track_sheets[5])
    spese_straordinarie = track_sheets[6]
    staff = clean_staff(melt_staff(staff_sheets[0]))


    incassi_mese = commerciale.loc[commerciale['Month'] == 'November', 'Paid'].sum()
    contratti_mese = commerciale.loc[commerciale['Month'] == 'November', 'Prezzo totale'].sum()
    spese_staff_mese = staff.loc[staff['Month'] == 'November', 'Instructor_earn'].sum()
    spese_mese = spese.loc[spese['Month'] == 'November', 'Valore'].sum() + spese_staff_mese
    utenti_mese = commerciale.loc[commerciale['Month'] == 'November', 'Paid'].count()
    lead_mese = trattative.loc[trattative['Month'] == 'November', 'Mail'].count()
    corsi_mese = corsi.loc[corsi['Month'] == 'November', 'Durata_hours'].count()
    private_mese = private.loc[private['Month'] == 'November', 'Durata_hours'].count()


    # Get interesting metrics
    metrics = {
        "month":"November",
        "incassi_mese" : incassi_mese ,
        "contratti_mese" :contratti_mese,   
        "spese_mese" :   spese_mese,
        "netto_mese" : incassi_mese - spese_mese,
        "utenti_mese" : utenti_mese, 
        "lead_mese" : lead_mese,
        "corsi_mese" :  corsi_mese,
        "private_mese" : private_mese,
        "spese_staff_mese" : spese_staff_mese
    }

    ### PLOTS ###
    # Incassi e contratti
    exclude_words = ["Rata","Commento","Cumulato","Group","month","Contratti","Utenti","Applicato","Pagato","Month"]
    fig_contratti =   standard_hist(commerciale, x="Data", y='Prezzo totale', title='Contratti stipulati', stack=False, legend_value="Servizio", exclude_words=exclude_words).to_html()
    fig_ricavi      = standard_hist(commerciale, x="Data", y='Paid', title='Cassa', stack=False, legend_value="Servizio", exclude_words=exclude_words).to_html()
    fig_contratti_monthly = standard_hist(commerciale, x="Month", y='Prezzo totale', title='Contratti stipulati', stack=True, legend_value="Servizio", exclude_words=exclude_words).to_html()
    fig_ricavi_monthly =    standard_hist(commerciale, x="Month", y='Paid', title='Cassa', stack=True, legend_value="Servizio", exclude_words=exclude_words).to_html()

    # cosa vendiamo?
    servizio_count = commerciale.groupby(['Servizio', 'Month']).size().reset_index(name='Count')
    fig_servizio_count = standard_hist(servizio_count, x="Month", y='Count', legend_value="Servizio", title='Servizio count').to_html()

    durata_count = commerciale.groupby(['Durata', 'Month']).size().reset_index(name='Count')
    fig_durata_count = standard_hist(durata_count, x="Month", y='Count', legend_value="Durata", title='Durata count').to_html()

    # stato rate
    commerciale_rate = commerciale[commerciale['Rateizzazione'] == 'Si']   ### Capire come funzionano le rate

    # Valore contratto per utente
    avg_data = commerciale.groupby('Month')["Contratti_month_m"].mean().reset_index()
    fig_value_user_monthly = standard_hist(avg_data, x="Month", y='Contratti_month_m',legend_value="Month", title='Average Contract Amount per User (Monthly)').to_html()
    # not used
    avg_data = commerciale.groupby('Month')["Contratti_month_y"].mean().reset_index()
    fig_value_user_year = standard_hist(avg_data, x="Month", y='Contratti_month_y', title='Average Contract Amount per User (Monthly)').to_html()

    # Numero clienti
    new_clients_data = commerciale.groupby('Month')["Utenti_month"].first().reset_index()
    fig_clienti = standard_hist(new_clients_data, x="Month", y='Utenti_month',legend_value="Month", title='Number of New Clients per Month').to_html()

    # Spese ricorrenti
    fig_spese_ricorrenti = standard_hist(spese, x="Month", y='Valore', title='Spese ricorrenti', legend_value="Tipo", stack=True).to_html()

    # corsi  e private per day
    fig_corsi = standard_hist(corsi, x="Data", y='Durata_hours', title='Corsi', legend_value="Classe", stack=False).to_html()
    fig_private = standard_hist(private, x="Data", y='Durata_hours', title='Private', legend_value="Istruttore", stack=False).to_html()

    # staff
    fig_staff_month = standard_hist(staff, x="Month", y='Instructor_earn', title='Salari staff', stack=True, legend_value="Instructor").to_html()
    fig_staff =    standard_hist(staff, x="Data", y='Instructor_earn', title='Salari staff', stack=False, legend_value="Instructor").to_html()

    commerciale_no_singolo = commerciale[~commerciale["Servizio"].isin(["Ingresso singolo", "Affitto", "Add here other columns"])]
    fig_scadenze = standard_hist(commerciale_no_singolo, x="Mese fine", y="Ones", title="Scadenze", legend_value="Servizio", stack=True, exclude_words=exclude_words).to_html()

    # leads
    #fig_leads = standard_hist(trattative, x="Data inizio trattativa", y='Count', title='Trattative', stack=False, legend_value="Provenienza lead", exclude_words=["azione"]).to_html()
    
    context = {
        "metrics":metrics,
        'fig_clienti': fig_clienti,
        'fig_ricavi': fig_ricavi,
        'fig_ricavi_monthly': fig_ricavi_monthly,
        'fig_contratti':fig_contratti,
        'fig_contratti_monthly':fig_contratti_monthly,       
        'fig_value_user_monthly': fig_value_user_monthly,
        'fig_value_user_year': fig_value_user_year,

        'fig_spese_ricorrenti':fig_spese_ricorrenti,
        'fig_corsi':fig_corsi,
        'fig_private':fig_private,

        'fig_staff_month':fig_staff_month,
        'fig_staff':fig_staff,

    
        #'fig_leads':fig_leads,
        "fig_servizio_count":fig_servizio_count,
        "fig_durata_count":fig_durata_count,

        "fig_scadenze":fig_scadenze



        }

    return render(request, 'home.html', context)
