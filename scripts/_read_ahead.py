import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

xl = pd.ExcelFile(r'C:\Users\oncel\Downloads\AHEAD_DigitalLibrary_26062323.xlsx')
print('Sayfalar:', xl.sheet_names)

for sh in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sh, nrows=3)
    print(f'\n=== {sh} === ({df.shape[1]} kolon)')
    print(list(df.columns))
    print(df.to_string())
