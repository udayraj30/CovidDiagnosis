class GetClinicalReports:
    def startClinicalReports(self):
        from .a_utils import (
            filter_patients,
            filter_pos,
            get_sym_severity,
            get_sym_severity_score,
            is_abnormal_cxr,
            open_data,
            plot_fill_rates,
            print_data_info,
            SYMPTOMS,
            VITALS,
        )

        data = open_data()
        print_data_info(data)

        plot_fill_rates(data)
        positive_patients = filter_pos(data)
        symptomatic_patients = filter_patients(data, SYMPTOMS)
        patients_w_vitals = filter_patients(data, VITALS, col_type='numeric')

        is_not_null = ~data['cxr_impression'].isnull()
        data.loc[is_not_null, 'is_abnormal_cxr'] = data.loc[
            is_not_null, 'cxr_impression'
        ].apply(lambda cxr: is_abnormal_cxr(cxr))

        data.loc[:, 'num_symptoms'] = data.loc[:, :].apply(
            lambda x: sum(1 for sym in SYMPTOMS if x[sym] == True), axis=1
        )
        data['severity_score'] = data.apply(
            lambda x: get_sym_severity_score(x), axis=1
        )
        data['sym_severity'] = data.severity_score.apply(
            lambda x: get_sym_severity(x)
        )
        import pandas as pd
        df = pd.read_csv('data/06-16_carbonhealth_and_braidhealth.csv')
        df = df[['batch_date','test_name','covid19_test_results','age','high_risk_exposure_occupation','diabetes','temperature','pulse','cough','sats']]
        df = df.to_html
        return df
