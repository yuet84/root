python info
		|
		|===MACD:											{
				|
				|---定义：									{
						|
						|...
						|
						|...DIFF = EMA("close", T=12) - EMA("close", T=26)；大概是14日线；
						|
						|...DEA = EMA("diff", T=9)；大概是20日线
						|
						|...BAR = ("diff" - "dea") * 2
						|
						|...0轴：大概是60日均线；
				}
				|
				|---应用：									{
						|
						|...DIFF跌破0轴，股价跌破60日均线；
						|
						|...红柱子对比前面一根不再伸长时，股价就会下跌；绿柱子对比前面一根不再伸长时，股价就会止跌；（提前）
						|
						|...底背离：下降趋势，创新低后，DIFF回抽0轴（a）0轴上；b）跌破0轴一点点；c）突破0轴一点点）后的背离：股价创新低，而DIFF不创新低；
							顶背离：上升趋势，创新高后，DIFF回抽0轴（a）0轴上；b）跌破0轴一点点；c）突破0轴一点点）后的背离：股价创新高，而DIFF不创新高；
				}
		}
		|
		|===
############
########################
####################################
########################################################################
12/26
24/52

买入点：	HMA_12金叉HMA26 && HMA_26非下降趋势
卖出点：	HMA_26下降趋势
HMA_35与HMA50的位置决定