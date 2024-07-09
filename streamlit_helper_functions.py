import streamlit as st
import pandas as pd

def convert_df(df):
	return df.to_csv(index=False).encode('utf-8')


