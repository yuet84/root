python info
		|
		|===pandas：										{
				|
				|---Create dataframe:						{
						|
						|...空dataframe：					df = pd.DataFrame()
				}
				|
				|---dataframe迭代:							{
						|
						|...按行展开 - df.iterrows():		{
															for index, row in df.iterrows():
															Param：
																	. index：	行索引名；
																	. row：		行pandas Series;
						}
						|
						|...按行展开 - df.itertuples():		{
															for row in df.itertuples():
															Param：
																	. row：		行tuples，索引具体元素row.Close;
						}
						|
						|...按列展开 - df.iteritems():		{
															for key, value in df.iteritems():
																print("Key: ", key, ";   value: ", value)
															Param:
																	. key:		列索引名；
																	. value：	该列的所有值
						}
				}
		}
		|
		|===
