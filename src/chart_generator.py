"""Generate publication figures from the saved Excel formula values."""
from results import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
NAVY='#19394D';TEAL='#147C77';GOLD='#A57439';GREY='#526976'
def build():
    p=ROOT/'charts';p.mkdir(exist_ok=True)
    years=['FY22','FY23','FY24','FY25','FY26']
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.labelcolor':GREY,'xtick.color':GREY,'ytick.color':GREY,'font.size':10})
    defs=[('01_revenue','Revenue from operations',[(IS,5,'Revenue')],False,False),('02_growth','Annual revenue growth',[(RA,5,'Growth')],True,False),('03_ebitda','Operating EBITDA and margin',[(IS,12,'EBITDA'),(RA,6,'EBITDA margin')],False,True),('04_profit','Group profit and net margin',[(IS,21,'Group PAT'),(RA,8,'Net margin')],False,True),('05_debt_cash','Debt and cash on hand',[(BS,25,'Borrowings + leases'),(BS,15,'Cash equivalents')],False,False),('06_cash_capex','Operating cash flow and capital expenditure',[(CF,5,'CFO'),(CF,6,'Cash capex')],False,False),('07_free_cash_flow','Three cash-flow measures',[(CF,15,'Cash after capex'),(CF,16,'FCFE proxy'),(RA,16,'UFCF proxy')],False,False),('08_returns','Return on capital and equity',[(RA,11,'ROE'),(RA,12,'ROIC')],True,False)]
    for key,title,lines,percent,twin in defs:
        fig,ax=plt.subplots(figsize=(8.5,4.5));axes=[ax];ax.axhline(0,color='#B8C8CC',lw=.8);ax.set_xticks(range(5),years);ax.set_ylabel('%' if percent else 'INR crore');ax.grid(axis='y',alpha=.14);ax.set_axisbelow(True)
        for j,(sheet,r,label) in enumerate(lines):
            vals=series(sheet,r);t=ax
            if twin and j:
                t=ax.twinx();axes.append(t);t.set_ylabel('Margin (%)',color=TEAL);t.yaxis.set_major_formatter(ticker.PercentFormatter(1))
            color=[NAVY,TEAL,GOLD][j]
            if twin and not j or len(lines)==1 and not percent:t.bar(range(5),vals,width=.54,color=color,label=label)
            else:t.plot(range(5),vals,marker='o',lw=2.5,color=color,label=label)
        if percent:ax.yaxis.set_major_formatter(ticker.PercentFormatter(1))
        handles=[];labels=[]
        for t in axes:
            h,l=t.get_legend_handles_labels();handles+=h;labels+=l
        fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.08),ncol=3,frameon=False)
        fig.subplots_adjust(left=.13,right=.87 if twin else .96,top=.84,bottom=.28)
        fig.text(.06,.92,title,weight='bold',fontsize=17,color=NAVY);fig.text(.06,.035,'Source: CEAT consolidated annual reports FY22–FY26; model calculations. FY ends 31 March.',fontsize=8,color=GREY)
        fig.savefig(p/(key+'.png'),dpi=165);plt.close(fig)
if __name__=='__main__':build()

