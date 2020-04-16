python info
		|
		|===移动平均线：									{
				|
				|---EMA(Exponential Moving Average):		{
						|
						|...定义:							EMA（today）= α * Price（today） + ( 1 - α ) * EMA（yesterday）
															Param:
																α:	平滑指数，一般取作2 / (N+1);
																EMA（0）= Price（0）;
						|
						|...pandas.Series.ewm():			Series.ewm(self, com=None, span=None, halflife=None, alpha=None, min_periods=0, adjust=True, ignore_na=False, axis=0)[source]
															Param:
																com:	定义α的一种方式， α = 1 / (1+com), for com≥0.
																span:	定义α的一种方式， α = 2 / (span+1), for span≥1.
																halflife:	定义α的一种方式， α = 1 − exp(log(0.5) / halflife),for halflife>0.
																alpha:	平滑因子, 0 < α ≤ 1.
																adjust:	True时，加权平均是按如下因子计算：(1-alpha)(n-1), (1-alpha)(n-2), …, 1-alpha, 1
																		False时，因子权重按如下当时计算：	weighted_average[0] = arg[0];
																											weighted_average[i] = (1-alpha)weighted_average[i-1] + alphaarg[i].
																ignore_na:	在加权计算中忽略Nan的值
															返回值: 为DataFrame
						|
						|...EMA计算：						Series.ewm(alpha=α, adjust=False, ignore_na=True)
															即：
																	y0 = x0,
																	yt = α * xt + (1 - α) * yt_1
																	Param:
																		α:	权重的衰减程度，取值在 0 和 1 之间。  越大，过去的观测值衰减的越快。
																			取值：2 / (T + 1)；或1 / T
				}
				|
				|---HMA(Hull Moving Average)：赫尔移动平均：{
						|
						|...HMA计算：						1.	计算窗口为 T / 2 的加权移动平均，并把结果乘以 2（如果 T / 2 不是整数则取整）
																df.Stock['Hshort'] = df.Stock['Close'].ewm(alpha=round(2/T), adjust=False) * 2
															2.	计算窗口为T的加权移动平均
																df.Stock['Hlong'] = df.Stock['Close'].ewm(alpha=T, adjust=False)
															3.	用第 1 步的结果减去第 2 部的结果，得到一个新的时间序列
																df.Stock['HMA'] = df.Stock['Hshort'] - df.Stock['Hlong']
															4.	以第 3 步得到的时间序列为对象，计算窗口为平方根(T)的加权移动平均（如果平方根(T)不是整数则取整）
																df.Stock['HMA'] = df.Stock['HMA'].ewm(alpha=round(T**0.5), adjust=False)
				}
		}