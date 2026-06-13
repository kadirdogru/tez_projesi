import pandas as pd
df = pd.read_excel('master_dataset.xlsx')
s = df[(df['yildiz'] == 0) & (df['platform'] == 'n11') & (df['kategori'] == 'robot_supurge')]
print(s['urun'].value_counts())