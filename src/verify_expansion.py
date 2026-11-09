"""Reconstruct funding, financial statements and the DCF separate from workbook formulas."""
import csv
import math
from statistics import median
from results import *
from committee import F,ND,FI,AF,PD,HEAD,outcome

def verify():
    count=0
    def eq(x,y):
        nonlocal count
        assert math.isclose(x,y,abs_tol=1e-6,rel_tol=1e-9),(x,y)
        count+=1
    def ok(test,msg):
        nonlocal count
        assert test,msg
        count+=1
    cases=['On time','Delay','External','Stress','Funded stress'];tax=v(AS,'B11')
    for r in range(21,40):ok(v('Model Checks','D'+str(r))=='PASS','live workbook control '+str(r))
    for ix,s in enumerate(cases,4):
        floor=v(FI,'B4');q=lambda r,c:v(s,c+str(r))
        prior_cash=v(BS,'H15');prior_debt=v(BS,'H23');prior_nwc=v(BS,'H27');prior_bridge=0;cash_unassisted=prior_cash
        paths=[];bridges=[];gross=[];funded=[];limits=[];cumulative=0
        for k in range(18):
            c=get_column_letter(k+3);p=get_column_letter(k+2);g=lambda r:q(r,c)
            eq(g(12)-sum(g(r) for r in [13,14,15,17,19,21]),g(22))
            eq(g(39),g(22)+g(17)+g(19)-(g(26)-prior_nwc))
            eq(g(40),-sum(g(r) for r in range(28,32)))
            eq(prior_cash+g(39)+g(40)+g(43),g(44))
            eq(prior_debt+g(36)+g(42)-g(34)-g(35)-g(37),g(48))
            eq(g(44)+g(23)+g(24)+g(50)+g(51),g(25)+g(48)+g(49)+g(53)+g(54))
            eq(g(18)*(1-tax)+g(17)-sum(g(r) for r in range(28,33))-g(27),g(59))
            eq(g(19),((q(45,p)+q(49,p))*v(FI,'B26')+prior_bridge*v(FI,'B27')+(q(46,p)+g(36))*v(FI,'B29'))/4)
            interest_saved=prior_bridge*v(FI,'B27')/4
            incremental_tax=(max(0,g(20)+interest_saved)-max(0,g(20)))*tax
            cash_unassisted+=g(39)+g(40)+g(43)-g(42)+interest_saved-incremental_tax
            eq(cash_unassisted,g(61));ok(g(44)>=floor-1e-7 and g(47)>=-1e-7,'cash floor / bridge')
            if k<6:
                paths.append(cash_unassisted);bridges.append(g(47));gross.append(g(48));funded.append(g(44));cumulative+=g(30)
                weight=g(62)
                limits.append(max(0,(cash_unassisted+cumulative-floor)/weight) if weight else (1e9 if cash_unassisted>=floor else 0))
            prior_cash,prior_debt,prior_nwc,prior_bridge=g(44),g(48),g(26),g(47)
        eq(max(bridges),v(F,'C'+str(ix)));eq(min(paths),v(F,'E'+str(ix)));eq(max(gross),v(F,'H'+str(ix)));eq(min(funded),v(F,'F'+str(ix)))
        eq(min(min(limits),v(FI,'B5')),v(F,'G'+str(ix)))
        first=next((q(3,get_column_letter(k+3)) for k,x in enumerate(paths) if x<floor-.001),'None')
        ok(first==v(F,'B'+str(ix)),'first model floor breach')
    for c in 'BCDEF':
        eq(v(AF,c+'23'),v(AF,c+'27'));eq(v(AF,c+'4')*v(AF,c+'35'),v(AF,c+'5'));eq(v(AF,c+'7')-v(AF,c+'8')+v(AF,c+'9')-v(AF,c+'11'),v(AF,c+'12'))
    for r in range(25,33):
        w,g,roic=[v(ND,c+str(r)) for c in 'EFG']
        explicit=sum(v(ND,'H'+str(i))/(1+w)**v(ND,'B'+str(i)) for i in range(4,22))
        terminal=v(AF,'F36')*(1+g)*(1-g/roic)/(w-g)/(1+w)**v(ND,'B21')
        eq((explicit+terminal-v(BS,'H31'))/v(TC,'C8'),v(ND,'H'+str(r)))
    eq(v(ND,'B64'),v(ND,'B36'));eq(v(ND,'B47'),v(TC,'B8'))
    eq(v(ND,'B43'),v(ND,'B37')+v(AF,'F4')*v(ND,'B41')*(1-tax))
    eq(v(ND,'B30'),v(ND,'B27')-v(ND,'B29'));eq(v(ND,'B29')*v(ND,'B26'),v(ND,'B27')*v(ND,'B25'))
    eq(v(ND,'B50'),v(ND,'B49')+(v(ND,'B51')-v(DC,'F7'))*v(DC,'F5')*(1-tax))
    for idx in range(3):
        rr=[v(TC,'O'+str(r)) for r in [5,6,7] if r!=idx+5];eq(median(rr),v(PD,'B'+str(idx+14)))
        eq(v(PD,'L'+str(idx+4)),v(TC,'K'+str(idx+5)))
    return count
if __name__=='__main__':print(verify(),'integrated underwriting tests passed.')

