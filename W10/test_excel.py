import pandas as pd

a1 = [0,1,2]
a2 = [3,4,5]
a3 = [10, 11, 12.3]
array = [a1, a2, a3]


df = pd.DataFrame(array).T
df.to_excel(excel_writer = "C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/mytest.xlsx")