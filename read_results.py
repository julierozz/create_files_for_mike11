from pandas import read_table

xychain=read_table("xychainage.txt",skipinitialspace=True,header=0,sep=4*'\s')
test=read_table("test-all.txt")