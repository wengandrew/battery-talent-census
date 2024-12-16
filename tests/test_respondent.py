import numpy as np
import pytest
import pandas as pd
from src.respondent import Respondent

@pytest.fixture
def resp():
    return Respondent('xgiqw1z6r37pu305hiipxgiqw11r00jc')

def test_respondent_initialization(resp):
    assert resp.respondent_id == 'xgiqw1z6r37pu305hiipxgiqw11r00jc'
    assert resp.df_gsh is None
    assert resp.df_typ is None
    assert resp.census is None
    assert resp.company is None
    assert resp.student is None
    assert not resp.is_working
    assert not resp.is_student
    assert not resp.is_unemployed

def test_set_properties_from_google_sheet(resp):
    df_gsh = pd.read_csv('data/talent_census_data_20241216_gsheet_export.csv')
    resp.set_properties_from_google_sheet(df_gsh)

    assert resp.df_gsh is not None
    assert resp.census['sentiment']['values'][0] == 5
    assert resp.is_working
    assert not resp.is_student
    assert not resp.is_unemployed

def test_set_properties_from_google_sheet_company(resp):
    df_gsh = pd.read_csv('data/talent_census_data_20241216_gsheet_export.csv')
    resp.set_properties_from_google_sheet(df_gsh)

    assert resp.company['company_satisfaction']['values'][0] == 4

def test_set_properties_from_google_sheet_student(resp):
    df_gsh = pd.read_csv('data/talent_census_data_20241216_gsheet_export.csv')
    resp.set_properties_from_google_sheet(df_gsh)


def test_set_properties_from_typeform(resp):
    df_typ = pd.read_csv('data/talent_census_data_20241216_typeform_export.csv')
    resp.set_properties_from_typeform(df_typ)

    assert resp.df_typ is not None
