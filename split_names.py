import pandas as pd

# Load the data #
df = pd.read_excel('input_names.xlsx')

#print(df['Name'])


def add_name(or_nm):
    if len(or_nm)>40:
        split_=or_nm.rfind(" ",0,40)
        if split_!=-1:
            return or_nm[split_:]
        else:
            return ("N/A")

def short_name(or_nm):

    if len(or_nm)>40:
        split2=or_nm.rfind(" ",0,40)
        if split2!=-1:
            return or_nm[:split2]
        else:
            return ("N/A")

original_name=[nm for nm in df['Name']]
additional_names=[add_name(nm) for nm in df['Name']]
names=[short_name(nm) for nm in df['Name']]

original_name=pd.Series(original_name)
additional_names=pd.Series(additional_names)
names=pd.Series(names)

df=pd.concat([df,names,additional_names],axis=1)

df.to_excel("names_split.xlsx")
