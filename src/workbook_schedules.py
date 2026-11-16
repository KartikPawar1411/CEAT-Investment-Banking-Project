"""Finish scenario, sensitivity, dashboard and check schedules in the supplied workbook."""
def finish(ns):
    globals().update(ns)
    w=wb[TC];lab(w,12,'MRF · Jun LTM (separate)')
    for c in range(2,10):put(w,12,c,'='+col(c)+'5')
    for c,s in [(10,'C'),(11,'J'),(12,'I'),(13,'H')]:
        put(w,12,c,'='+ref(PE,s+'5')+'+'+ref(PE,s+'13')+'-'+ref(PE,s+'12'))
    for c,num,den in [(14,'I','J'),(15,'I','K'),(16,'I','L'),(17,'D','M')]:
        put(w,12,c,f'=IF({den}12>0,{num}12/{den}12,"NM")',X)
    put(w,12,19,'=K12/J12',PC)
    w=wb[SC];header(w,4,['Case','Growth Δ','Margin Δ','WACC Δ','g Δ','₹/share','vs close'])
    for r,(k,v) in enumerate(A['risk_cases'].items(),5):
        row(w,r,[k.title()]+v)
        for c in range(2,6):w.cell(r,c).number_format=PC
    w=wb[SE];header(w,4,['WACC ↓   /   perpetual g →']+['g '+s for s in ['−100bp','−50bp','base','+50bp','+100bp']])
    for c,d in enumerate([-.01,-.005,0,.005,.01],2):
        put(w,5,c,'='+ref(AS,'B12')+f'+({d})',PC)
    for r,d in enumerate([-.02,-.01,0,.01,.02],6):
        put(w,r,1,'='+ref(WA,'B18')+f'+({d})',PC)
        for c in range(2,7):
            a=col(c);cost=f'$A{r}';g=f'{a}$5'
            pv='SUM('+','.join(ref(DC,k+'18')+'/((1+'+cost+')^'+ref(DC,k+'20')+')' for k in 'BCDEF')+')'
            tv=ref(DC,'F15')+'*(1+'+g+')/('+cost+'-'+g+')/(1+'+cost+')^'+ref(DC,'F20')
            put(w,r,c,f'=IF({cost}>{g},({pv}+{tv}-'+ref(DC,'B30')+')/'+ref(DC,'B32')+',"NM")')
    header(w,14,['Growth Δ ↓   /   margin Δ →','−200bp','−100bp','Base','+100bp','+200bp'])
    for c,d in enumerate([-.02,-.01,0,.01,.02],2):put(w,15,c,d,PC)
    for r,d in enumerate([-.04,-.02,0,.02,.04],16):put(w,r,1,d,PC)
    o=wb[OS];header(o,4,['Case','Growth Δ','Margin Δ','WACC','g','Year','Revenue','EBITDA','D&A','EBIT','Capex','Closing NWC','Annual UFCF','Future UFCF','PV future','PV terminal','₹ / share'])
    names=['Bear','Base','Bull']+[f'G{i+1} M{j+1}' for i in range(5) for j in range(5)]
    for idx,name in enumerate(names):
        start=5+idx*5;end=start+4
        for i in range(5):
            r=start+i;a=col(2+i);l=lambda s,addr:ref(s,addr)
            if idx<3:
                cr=5+idx;gr=l(SC,'B'+str(cr));mg=l(SC,'C'+str(cr));wd=l(SC,'D'+str(cr));gd=l(SC,'E'+str(cr))
            else:
                ri,ci=divmod(idx-3,5);gr=l(SE,'A'+str(16+ri));mg=l(SE,col(2+ci)+'15');wd='0';gd='0'
            row(o,r,[name,'='+gr,'='+mg,'='+l(WA,'B18')+'+'+wd,'='+l(AS,'B12')+'+'+gd,'FY'+str(27+i)])
            for c in range(2,6):o.cell(r,c).number_format=PC
            rev=(l(IS,'H5')+'+('+l(IS,'F5')+'-'+l(IS,'I5')+')*(1+'+l(AS,'B16')+f'+B{r})') if i==0 else f'G{r-1}*(1+'+l(AS,a+'16')+f'+B{r})'
            ebitda=(l(IS,'H12')+f'+(G{r}-'+l(IS,'H5')+')*('+l(AS,a+'17')+f'+C{r})') if i==0 else f'G{r}*('+l(AS,a+'17')+f'+C{r})'
            capex=l(AS,'B19') if i==0 else f'G{r}*'+l(AS,a+'19')
            prev=l(BS,'F27') if i==0 else f'L{r-1}'
            annual=f'J{r}*(1-'+l(AS,'B11')+f')+I{r}-K{r}-L{r}+'+prev
            future=(f'((J{r}-'+l(IS,'H14')+')*(1-'+l(AS,'B11')+f')+I{r}-'+l(IS,'H13')+f'-K{r}+'+l(CF,'H6')+f'-L{r}+'+l(BS,'H27')+')*'+l(DC,'B17')) if i==0 else f'M{r}'
            for c,f in [(7,rev),(8,ebitda),(9,f'G{r}*'+l(AS,a+'18')),(10,f'H{r}-I{r}'),(11,capex),(12,f'G{r}*'+l(AS,a+'20')),(13,annual),(14,future),(15,f'N{r}/(1+D{r})^'+l(DC,a+'20'))]:put(o,r,c,'='+f)
            if i==4:
                put(o,r,16,f'=IF(D{r}>E{r},M{r}*(1+E{r})/(D{r}-E{r})/(1+D{r})^'+l(DC,'F20')+',"NM")')
                put(o,r,17,f'=IF(ISNUMBER(P{r}),(SUM(O{start}:O{r})+P{r}-'+l(DC,'B30')+')/'+l(DC,'B32')+',"NM")')
        if idx<3:
            link(wb[SC],5+idx,6,OS,'Q'+str(end));put(wb[SC],5+idx,7,f'=F{5+idx}/'+ref(TC,'B8')+'-1',PC)
        else:link(wb[SE],16+ri,2+ci,OS,'Q'+str(end))
    w=wb[VS];header(w,4,['Valuation in INR per share','Low','Central','High','Central vs close'])
    for i in range(4):
        r=5+i;lab(w,r,['FY26 EV / sales','FY26 EV / EBITDA','FY26 EV / EBIT','FY26 P/E'][i])
        for c,k in [(2,'H'),(3,'I'),(4,'J')]:link(w,r,c,RV,k+str(r))
    lab(w,9,'DCF: operating & WACC scenarios')
    for c,i in enumerate([5,6,7],2):link(w,9,c,SC,'F'+str(i))
    for r in range(5,10):put(w,r,5,f'=C{r}/'+ref(TC,'B8')+'-1',PC)
    lab(w,11,'Market close · 6 November 2026');link(w,11,2,TC,'B8')
    w=wb[D];header(w,4,['CEAT Limited   •   NSE CEATLTD','Headline','Interpretation / source'])
    for r,(l,s,addr,fmt,note) in enumerate([
        ('Valuation date',AS,'B5',DATE,'Independent academic simulation, November 2026'),
        ('NSE closing price (₹)',TC,'B8',N,'Unadjusted EQ closing price'),
        ('FY26 revenue',IS,'F5',N,'Consolidated audited'),
        ('H1 FY27 revenue',IS,'H5',N,'Six months to 30 September 2026'),
        ('H1 FY27 cash after capex',CF,'H15',N,'Before interest, lease payments and financing flows'),
        ('FY26 EV / EBITDA peer IQR: low',RV,'H6',N,'₹ per share, three listed manufacturers'),
        ('FY26 EV / EBITDA peer IQR: high',RV,'J6',N,'Inclusive 25th to 75th percentiles'),
        ('Base DCF (₹ per share)',DC,'B33',N,'Nominal INR perpetuity DCF, end-period stub'),
        ('Base DCF vs NSE close',DC,'B34',PC,'Model difference from the observed price'),
        ('Base WACC',WA,'B18',PC,'Market equity / gross debt weighting'),
        ('Market capitalization',TC,'D8',N,'₹ crore, 4.0450092 crore listed shares'),
        ('Enterprise value',TC,'I8',N,'After cash, leases, NCI and non-operating assets'),
        ('52-week price performance',MP,None,PC,'Price return, excludes dividends')],5):
        lab(w,r,l)
        if addr:link(w,r,2,s,addr,fmt)
        else:put(w,r,2,'='+ref(MP,'B'+str(last))+'/'+ref(MP,'B5')+'-1',PC)
        w.cell(r,3,note)
    w.column_dimensions['C'].width=62
    w=wb[QC];header(w,4,['Test','Residual','Tolerance','Result'])
    tests=[('Annual balance sheet',f'MAX('+','.join('ABS('+ref(BS,c+'30')+')' for c in 'BCDEF')+')',.02),
        ('Annual income reconciliation','MAX('+','.join('ABS('+ref(IS,c+'23')+')' for c in 'BCDEF')+')',.02),
        ('Annual cash reconciliation','MAX('+','.join('ABS('+ref(CF,c+'17')+')' for c in 'BCDEF')+')',.02),
        ('H1 balance sheet',ref(BS,'H30'),1),('H1 and quarter income rounding','MAX('+','.join('ABS('+ref(IS,c+'23')+')' for c in 'GHI')+')',2),
        ('H1 cash reconciliation',ref(CF,'H17'),1),('WACC weights sum',ref(WA,'B16')+'+'+ref(WA,'B17')+'-1',1e-8),
        ('Base operating sensitivity tie',ref(SE,'D18')+'-'+ref(DC,'B33'),1e-6),('Base WACC/g tie',ref(SE,'D8')+'-'+ref(DC,'B33'),1e-6),('Base scenario tie',ref(SC,'F6')+'-'+ref(DC,'B33'),1e-6),
        ('Enterprise to equity',ref(TC,'I8')+'-'+ref(BS,'H31')+'-'+ref(TC,'D8'),1e-6),('WACC exceeds g','IF('+ref(WA,'B18')+'>'+ref(AS,'B12')+',0,1)',0)]
    for r,(t,e,tol) in enumerate(tests,5):row(w,r,[t,'='+e,tol,f'=IF(ABS(B{r})<=C{r},"PASS","CHECK")'])
    chart_sheet=wb[CH]
    options=[('Revenue · ₹ crore',IS,[5]),('Revenue growth · %',RA,[5]),('EBITDA · ₹ crore',IS,[12]),('EBITDA and PAT margins · %',RA,[6,8]),('Group PAT · ₹ crore',IS,[21]),('Gross debt and cash · ₹ crore',BS,[25,15]),('CFO and capex · ₹ crore',CF,[5,6]),('Cash after capex and UFCF · ₹ crore',CF,[15]),('ROE and ROIC · %',RA,[11,12])]
    for i,(title,src,rows) in enumerate(options):
        start=5+i*4
        for j in range(5):chart_sheet.cell(start,2+j,periods[j])
        for h,rr in enumerate(rows,1):
            lab(chart_sheet,start+h,wb[src].cell(rr,1).value)
            for j in range(5):link(chart_sheet,start+h,2+j,src,col(2+j)+str(rr),PC if '%' in title else N)
        if i==7:
            lab(chart_sheet,start+2,'UFCF proxy')
            for j in range(5):link(chart_sheet,start+2,2+j,RA,col(2+j)+'16')
        chart=LineChart();chart.title=title;chart.y_axis.title='Percent' if '%' in title else 'INR crore';chart.y_axis.numFmt='0%' if '%' in title else '#,##0';chart.style=13
        chart.add_data(Reference(chart_sheet,min_col=1,max_col=6,min_row=start+1,max_row=start+(2 if i==7 else len(rows))),titles_from_data=True,from_rows=True)
        chart.set_categories(Reference(chart_sheet,min_col=2,max_col=6,min_row=start));chart.width=16;chart.height=8.0;chart_sheet.add_chart(chart,'H'+str(4+i*18))
    for w in wb:
        w.sheet_view.zoomScale=85
        for cells in w.iter_rows():
            for v in cells:
                if v.value is None or v.row<=2 or v.fill.patternType=='solid':continue
                val=v.value;colr='172E3E'
                if v.data_type=='f':colr='008342' if '!' in val else '000000'
                elif isinstance(val,(int,float,dt.date)):colr='164BC0'
                if v.font.bold:continue
                v.font=Font(name='Calibri',size=11,color=colr)
                if isinstance(val,(float,int)) and v.number_format=='General':v.number_format=N
        w.merge_cells('A1:F1');w.merge_cells('A2:I2');w['A1'].fill=PatternFill('solid',fgColor='15374D');w['A1'].font=Font(name='Calibri',size=19,bold=True,color='FFFFFF')
        w['A1'].alignment=Alignment(vertical='center',indent=1);w['A2'].font=Font(name='Calibri',italic=True,color='506C77',size=11);w['A2'].alignment=Alignment(vertical='center',wrap_text=True)
        w.print_options.horizontalCentered=True;w.sheet_view.showGridLines=False
    for sn,rs in [(D,[10,11,12]),(DC,[15,22,29,31,33]),(WA,[18]),(IS,[12,14,21]),(BS,[26,31]),(CF,[15,16]),(VS,[9,11])]:
        for r in rs:
            for p in wb[sn][r][:min(wb[sn].max_column,9)]:
                p.fill=PatternFill('solid',fgColor='DDEFEF')
    for sn in [IS,BS,CF,RA]:
        w=wb[sn];w['A34']='Source by period';row(w,35,['PDF page(s)','AR23 126–127','AR23 126–127','AR24 122–123','AR26 138–139','AR26 138–139','H1 pp16–18','H1 pp16–18','H1 pp16–18'])
    w=wb[PE];header(w,40,['Strategic alternative','Value','Fit','Capital efficiency','Ease of execution','Risk containment','Speed','Long-term growth','Weighted score / 5'])
    row(w,41,['Analyst weights',.20,.20,.15,.10,.15,.10,.10])
    ratings=[('Staged organic expansion',[4,5,3,4,4,4,5]),('Acquire a business',[4,3,1,1,1,2,4]),('Raise standalone capital',[2,3,3,4,3,4,2]),('Distribution / technology JV',[3,4,5,3,4,3,4]),('Merger / strategic sale',[3,2,2,1,2,1,3])]
    for r,(k,arr) in enumerate(ratings,42):
        row(w,r,[k]+arr+[f'=SUMPRODUCT(B{r}:H{r},$B$41:$H$41)'])
    for c in range(2,9):w.cell(41,c).number_format=PC
    header(w,49,['Industry evidence','Value','Unit','Period / nature','Source'])
    for r,arr in enumerate([['Indian tyre turnover',100000,'INR cr','FY25 estimate','ATMA'],['Tyre exports',25057,'INR cr','FY25','EXPORT'],['Tyre exports',27312,'INR cr','FY26','EXPORT'],['Passenger vehicle sales',46.43,'lakh vehicles','FY26','SIAM'],['Commercial vehicle sales',10.80,'lakh vehicles','FY26','SIAM'],['Two-wheeler sales',2.17,'crore vehicles','FY26','SIAM'],['Domestic tyre demand growth low',.05,'growth','FY27 forecast','ICRA'],['Domestic tyre demand growth high',.07,'growth','FY27 forecast','ICRA']],50):row(w,r,arr)
    for r in [56,57]:w.cell(r,2).number_format=PC
    header(w,60,['CEAT ownership','% of issued shares','As at 30 Sep 2026'])
    for r,(t,v) in enumerate([('Promoter and promoter group',.4729),('Public incl. institutions',.5237),('Employee trust',.0034)],61):
        row(w,r,[t,v,'SHP, Table I']);w.cell(r,2).number_format=PC
    for r,t,v in [(65,'Domestic institutions within public',.2326),(66,'Foreign institutions within public',.1341)]:
        row(w,r,[t,v,'SHP, Table III']);w.cell(r,2).number_format=PC
    wb[IS]['J4']='Q2 FY26';put(wb[IS],5,10,3773);put(wb[IS],21,10,186);put(wb[IS],22,10,186)
    wb[IS]['J35']='H1 p16, selected comparator'
    put(wb[RA],5,7,'='+ref(IS,'G5')+'/'+ref(IS,'J5')+'-1',PC)
    w=wb[DC];lab(w,37,'FY31 UFCF required at market EV¹')
    put(w,37,2,'=('+ref(TC,'I8')+'-B25)/F21*('+ref(WA,'B18')+'-B26)/(1+B26)')
    lab(w,38,'Required uplift over forecast');put(w,38,2,'=B37/F15-1',PC)
    lab(w,40,'¹ Holds explicit cash flows, WACC and g fixed. This is a reverse DCF diagnostic.')
    wb[PE].column_dimensions['D'].width=34
    wb[SC].column_dimensions['A'].width=30
    wb[TC].freeze_panes='B5';wb[AS].freeze_panes='B5';wb.active=0
    from investment_decision import upgrade
    upgrade(wb)
    from ncd_case import add_ncd
    add_ncd(wb)
    OUT.parent.mkdir(exist_ok=True);wb.save(OUT)

