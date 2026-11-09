"""Write an editable 18-slide investment banking pitch book from recalculated Excel results."""
from results import *
from decision_slides import place
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_MARK
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
import math
NAVY='17374C'; DEEP='102C40'; TEAL='087D76'; GOLD='9A713E';GRAY='526874';PALE='E8F2F1';LIGHT='F1F4F5';WHITE='FFFFFF';BLACK='19303F';LINE='C7D4D7'
rgb=RGBColor.from_string
IN=Inches
R=Presentation();R.slide_width=IN(13.333);R.slide_height=IN(7.5)
def box(s,x,y,w,h,fill):
    q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,IN(x),IN(y),IN(w),IN(h));q.fill.solid();q.fill.fore_color.rgb=rgb(fill);q.line.fill.background();return q
def txt(s,x,y,w,h,t,size=15,color=BLACK,bold=False,align=None):
    q=s.shapes.add_textbox(IN(x),IN(y),IN(w),IN(h));tf=q.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=IN(.01);tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(str(t).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Calibri';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(0)
        if align:p.alignment=align
    return q
def base(title,section,source,insight=None):
    s=R.slides.add_slide(R.slide_layouts[6]);num=len(R.slides)
    txt(s,.55,.30,11,.24,section.upper(),10,TEAL,True)
    txt(s,.55,.66,12.2,.83,title,27,NAVY,True)
    box(s,.56,1.57,12.18,.018,LINE)
    if insight:
        box(s,.57,6.24,.047,.45,TEAL);txt(s,.73,6.24,11.97,.49,insight,13,NAVY,True)
    box(s,.56,6.94,12.19,.012,LINE)
    txt(s,.56,7.02,11.72,.32,source,8.7,GRAY)
    txt(s,12.1,7.02,.6,.23,f'{num:02d}',10,TEAL,True,PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text=source+'\nSee the source register and research report for original URLs and methods.'
    return s
def label(s,x,y,t,w=6):txt(s,x,y,w,.26,t,12,TEAL,True)
def note(s,x,y,w,title,body):
    txt(s,x,y,w,.34,title,17,NAVY,True);txt(s,x,y+.43,w,.82,body,13.3,GRAY)
def table(s,x,y,width,height,headers,rows,ratios=None,size=14,emph=None):
    nr=len(rows)+1;nc=len(headers);shape=s.shapes.add_table(nr,nc,IN(x),IN(y),IN(width),IN(height));t=shape.table;t.first_row=False;t.banded_rows=False
    if ratios:
        for c,k in enumerate(ratios):t.columns[c].width=IN(width*k/sum(ratios))
    for r,vals in enumerate([headers]+rows):
        t.rows[r].height=IN(height/nr)
        for c,val in enumerate(vals):
            cell=t.cell(r,c);cell.text=str(val);cell.margin_left=IN(.10);cell.margin_right=IN(.07);cell.margin_top=IN(.035);cell.margin_bottom=IN(.03);cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid();cell.fill.fore_color.rgb=rgb(NAVY if r==0 else PALE if emph is not None and r==emph else LIGHT if r%2 else WHITE)
            for p in cell.text_frame.paragraphs:
                p.font.name='Calibri';p.font.size=Pt(size if r else max(10,size-1));p.font.bold=(r==0 or c==0 or r==emph);p.font.color.rgb=rgb(WHITE if r==0 else BLACK);p.space_after=Pt(0)
    return shape
def chart(s,x,y,w,h,categories,data,kind=XL_CHART_TYPE.COLUMN_CLUSTERED,fmt='#,##0',maxval=None,minval=None):
    cd=CategoryChartData();cd.categories=categories
    for k,vals in data:cd.add_series(k,vals,number_format=fmt)
    ch=s.shapes.add_chart(kind,IN(x),IN(y),IN(w),IN(h),cd).chart
    ch.has_legend=len(data)>1
    if ch.has_legend:ch.legend.position=XL_LEGEND_POSITION.BOTTOM;ch.legend.include_in_layout=False;ch.legend.font.name='Calibri';ch.legend.font.size=Pt(10)
    ch.has_title=False;ch.font.name='Calibri';ch.font.size=Pt(11)
    for axis in [ch.category_axis,ch.value_axis]:
        axis.tick_labels.font.size=Pt(10);axis.tick_labels.font.color.rgb=rgb(GRAY);axis.major_tick_mark=XL_TICK_MARK.NONE;axis.minor_tick_mark=XL_TICK_MARK.NONE
        axis.format.line.color.rgb=rgb(LINE)
    ax=ch.value_axis;ax.tick_labels.number_format=fmt;ax.has_major_gridlines=True;ax.major_gridlines.format.line.color.rgb=rgb('DCE5E6');ax.major_gridlines.format.line.width=Pt(.6)
    if maxval is not None:ax.maximum_scale=maxval
    if minval is not None:ax.minimum_scale=minval
    for j,ss in enumerate(ch.series):
        color=[TEAL,NAVY,GOLD][j%3];ss.format.fill.solid();ss.format.fill.fore_color.rgb=rgb(color);ss.format.line.color.rgb=rgb(color)
        if kind==XL_CHART_TYPE.LINE_MARKERS:ss.format.line.width=Pt(2.7)
    return ch
def stat(s,x,y,w,amount,head,body):
    txt(s,x,y,w,.64,amount,34,TEAL,True);txt(s,x,y+.77,w,.37,head,16,NAVY,True);txt(s,x,y+1.23,w,.95,body,14,GRAY)
def football(s):
    x=.92;y=2.0;w=8.06;h=3.35;maxp=5000
    def yy(value):return y+h-h*value/maxp
    for value in range(0,5001,1000):
        py=yy(value);box(s,x,py,w,.009,LINE);txt(s,.35,py-.10,.5,.20,str(value//1000)+'k' if value else '0',9,GRAY,False,PP_ALIGN.RIGHT)
    for i,r in enumerate(range(5,10)):
        xx=x+.78+i*1.58;lo,mid,hi=series(VS,r,'BCD');color=TEAL if i<4 else GOLD
        box(s,xx-.15,yy(hi),.30,yy(lo)-yy(hi),color);box(s,xx-.23,yy(mid)-.018,.46,.036,DEEP)
        txt(s,xx-.65,y+h+.13,1.32,.47,['EV / sales','EV / EBITDA','EV / EBIT','P/E','DCF'][i],11,NAVY,True,PP_ALIGN.CENTER)
    price_y=yy(v(TC,'B8'));box(s,x,price_y,w,.023,'A74732')
def build():
    s=R.slides.add_slide(R.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(DEEP)
    box(s,.67,.75,.62,.06,'72C1B7');txt(s,.68,1.05,11,.30,'INDIA  /  AUTOMOBILE COMPONENTS',12,'98C6C6',True)
    txt(s,.65,1.91,12,1.0,'CEAT LIMITED',53,WHITE,True)
    txt(s,.70,3.01,11.8,1.16,'Strategic advisory, corporate valuation\nand growth opportunities',30,WHITE)
    txt(s,.72,4.53,11,.45,'Investment Banking Pitch Book  |  Valuation as of 6 November 2026',18,'ACD0D0')
    box(s,.71,6.45,11.93,.018,'55707E')
    txt(s,.71,6.66,10.7,.55,'November 2026  ·  Independent academic simulation  ·  NSE CEATLTD  /  BSE 500878',11,'C0D2D7');txt(s,12.01,6.68,.62,.34,'01',12,WHITE,True,PP_ALIGN.RIGHT)
    fy=['FY22','FY23','FY24','FY25','FY26'];future=['FY27E','FY28E','FY29E','FY30E','FY31E']
    place(2,(base,table,stat,note,txt))
    place(3,(base,table,stat,note,txt))
    s=base('Replacement accounts for half of standalone H1 sales','Revenue composition','CEAT Q2 FY27 investor presentation p7 (standalone mix); FY26 integrated report, consolidated geographic disclosures.',
        f'Consolidated customers outside India represented {pct(v(PE,"C37"))} of FY26 contract sales. That geographic measure has a different perimeter from standalone exports.')
    label(s,.68,1.84,'Standalone sales by customer channel');label(s,6.62,1.84,'Standalone sales by product')
    chart(s,.61,2.24,5.70,3.58,['Replacement','OEM','Exports'],[('Share',[.50,.30,.20])],fmt='0%',maxval=.60,minval=0)
    chart(s,6.45,2.24,6.20,3.58,['2/3W','Truck/bus','PC/UV','Off-highway','LCV/other'],[('Share',[.28,.27,.23,.16,.06])],fmt='0%',maxval=.35,minval=0)
    s=base(f'Revenue grew {pct(v(RA,"B20"))} a year from FY22 to FY26','Historical revenue','CEAT consolidated annual reports FY22–FY26; FY21 opening comparator in FY22 annual report. INR crore unless noted.',
        'FY26 growth includes acquired CAMSO sales. H1 FY27 also benefited from price increases, so the reported growth rate should not be extrapolated as volume growth.')
    label(s,.69,1.85,'Revenue from operations  ·  INR crore');chart(s,.59,2.22,7.12,3.65,fy,[('Revenue',series(IS,5))],minval=0,maxval=18000)
    table(s,8.02,2.02,4.59,3.77,['Year','Revenue','Growth'],[[fy[i],n(series(IS,5)[i]),pct(series(RA,5)[i])] for i in range(5)],size=14,emph=5)
    s=base('H1 operating margin fell as higher tyre prices lagged input costs','Profitability','CEAT annual reports FY22–FY26 and H1 filing; October earnings call. EBITDA excludes other income and equity-accounted profit.',
        f'FY26 ROIC was {pct(v(RA,"F12"))}, versus a {pct(v(WA,"B18"))} valuation-date WACC. Management reported another 8–9% sequential rise in Q2 raw-material costs.')
    label(s,.66,1.83,'Operating EBITDA and net margins');chart(s,.60,2.16,6.76,3.66,fy,[('Operating EBITDA %',series(RA,6)),('Net margin %',series(RA,8))],XL_CHART_TYPE.LINE_MARKERS,'0%',.16,0)
    table(s,7.65,1.99,5.02,3.95,['INR crore / %','FY26','H1 FY26','H1 FY27'],[[l]+[f(v(sh,k+str(r))) for k in 'FIH'] for l,sh,r,f in [('EBITDA',IS,12,n),('EBITDA margin',RA,6,pct),('Group PAT',IS,21,n),('Net margin',RA,8,pct),('Finance cost',IS,15,n)]],ratios=[1.5,1,1,1],size=12.6)
    s=base('H1 capex exceeded operating cash by ₹464 crore','Balance sheet and cash flow','CEAT consolidated cash-flow and balance sheets, FY22–FY26 and H1 FY27. Capex excludes acquisition consideration.',
        'September net debt including leases was ₹4,033 crore. Trade working capital grew as inventory reached ₹2,597 crore, up ₹814 crore from March.')
    label(s,.68,1.83,'Full-year cash generation and investment  ·  INR crore');chart(s,.61,2.21,7.13,3.66,fy,[('CFO',series(CF,5)),('Cash capex',series(CF,6))],minval=0)
    table(s,7.95,2.04,4.74,3.78,['INR crore','Mar 26','Sep 26'],[[l,*[n(x) for x in series(BS,r,'FH')]] for l,r in [('Borrowings',23),('Lease debt',24),('Cash',15),('Trade NWC',27),('Net debt',26)]],ratios=[1.4,1,1],size=14,emph=5)
    s=base('Domestic tyre demand is growing, but input costs threaten margins','Indian tyre market','ATMA FY25 estimated turnover; IBEF 4 Jun 2026; SIAM 14 Apr 2026; ICRA sector update 30 Sep 2026.',
        'ICRA expected 5–7% domestic tyre demand growth and roughly 200 bp of margin compression in FY27. These forecasts refer to the sector.')
    stat(s,.63,1.94,3.84,'₹1 lakh cr','FY25 industry turnover','ATMA estimate. Manufacturer revenues include overseas operations, limiting market-share comparisons.')
    stat(s,4.65,1.94,3.83,'₹27,312 cr','FY26 tyre exports','Up 9% from ₹25,057 crore in FY25. Export mix adds currency and logistics exposure.')
    stat(s,8.70,1.94,3.83,'15.4%','Q1 FY27 sample sales growth','ICRA attributed much of the revenue increase to price rises as manufacturers passed on input inflation.')
    table(s,.64,4.71,12.02,.91,['FY26 domestic vehicle sales','Passenger vehicles','Commercial vehicles','Two-wheelers'],[['SIAM volume / YoY','46.43 lakh / +7.9%','10.80 lakh / +12.6%','2.17 crore / +10.7%']],size=13)
    s=base('Three diversified tyre manufacturers anchor the primary peer set','Competitive positioning','FY26 consolidated filings of CEAT, MRF, Apollo and JK Tyre; issuer annual reports. Selection reflects analyst judgment.',
        'Balkrishna is a specialty reference, TVS Srichakra skews to two-wheelers and off-highway, and Goodyear India has a narrower farm-tyre profile.')
    table(s,.63,1.96,12.00,3.88,['Company','Operating fit','Distinction affecting comparability'],[
        ['MRF','Broad domestic replacement and OEM range','Larger scale and liquid investments. March is the latest verified balance sheet used.'],
        ['Apollo Tyres','Diversified passenger and commercial tyres','European exposure and FY26 restructuring and tax items affect earnings.'],
        ['JK Tyre','Closest on FY26 revenue, strong truck and bus overlap','Higher leverage and Mexico operations. Prior interim comparatives were restated.'],
        ['CEAT','Two-wheeler, replacement and specialty exposure','CAMSO changes mix and introduces execution risk during the ramp.']],ratios=[1,2.1,3.55],size=14,emph=4)
    s=base('CEAT grew faster than the three peers in FY26','Peer financial comparison','FY26 consolidated issuer filings; prior-year revenue from MRF annual report, Apollo 14 May release and JK restated results. INR crore.',
        'CEAT’s operating margin exceeded JK Tyre’s and trailed MRF and Apollo. Product mix and cost structure limit what a revenue multiple can explain.')
    table(s,.62,2.00,12.03,3.62,['Issuer','FY26 sales','Growth','Operating EBITDA','EBITDA margin','Parent PAT'],[[co,n(v(TC,'J'+str(r))),pct(v(TC,'R'+str(r))),n(v(TC,'K'+str(r))),pct(v(TC,'S'+str(r))),n(v(TC,'M'+str(r)))] for co,r in [('MRF',5),('Apollo Tyres',6),('JK Tyre',7),('CEAT',8)]],ratios=[1.4,1,1,1.5,1.15,1.12],size=15,emph=4)
    s=base(f'CEAT trades at {mult(v(TC,"O8"))} FY26 EBITDA versus a {mult(v(TC,"C17"))} peer median','Trading comparables','Market prices: NSE 6 Nov 2026. Issuer FY26 results and latest available balance sheets. Detailed bridge in Trading Comps.',
        f'The {pct(v(TC,"C21"))} premium on EV/EBITDA reflects the observed cross-section. The September LTM peer median of {mult(v(TC,"C27"))} uses only Apollo and JK Tyre.')
    table(s,.62,1.98,12.03,3.92,['Company','Mkt cap, ₹ cr','EV, ₹ cr','EV / sales','EV / EBITDA','EV / EBIT','P/E'],[[co,n(v(TC,'D'+str(r))),n(v(TC,'I'+str(r))),*[mult(x) for x in series(TC,r,'NOPQ')]] for co,r in [('MRF',5),('Apollo Tyres',6),('JK Tyre',7),('CEAT',8)]]+[['Peer median','—','—',*[mult(x) for x in series(TC,17,'BCDE')]]],ratios=[1.4,1.23,1.2,1,1.2,1.1,.92],size=13.5,emph=4)
    s=base(f'Peer EBITDA multiples imply {price(v(VS,"B6"))}–{price(v(VS,"D6"))} per share','Relative valuation','Analyst calculations. Three FY26 peers; low/high are inclusive peer quartiles. NSE close ₹3,545.80 on 6 Nov 2026.',
        f'Applying {mult(v(TC,"C17"))} to FY26 operating EBITDA gives EV of ₹{n(v(RV,"F6"))} crore. Deduct ₹{n(v(BS,"H31"))} crore of net claims to reach equity value.')
    table(s,.64,2.00,12.00,3.64,['FY26 method','P25 ₹/sh','Median ₹/sh','P75 ₹/sh','Median vs close'],[[l,*[n(x) for x in series(VS,r,'BCD')],pct(v(VS,'E'+str(r)))] for r,l in [(5,'EV / revenue'),(6,'EV / EBITDA'),(7,'EV / EBIT'),(8,'P/E')]],ratios=[1.65,1,1.2,1,1.5],size=15,emph=2)
    place(13,(base,table,stat,note,txt))
    place(14,(base,table,stat,note,txt))
    place(15,(base,table,stat,note,txt))
    s=base('Staged expansion scores highest, followed by a distribution partnership','Strategic alternatives','Analyst judgments. Weighted scores use seven criteria and 1–5 ratings; full decision matrix and acquisition screens in report.',
        'TVS Srichakra and Indag Rubber illustrate product adjacency. Availability, purchase prices, financing terms and transaction discussions are unverified.')
    table(s,.62,1.95,12.04,3.95,['Alternative','Score / 5','Financial and execution implications'],[[v(PE,'A'+str(r)),f'{v(PE,"I"+str(r)):.2f}',t] for r,t in [(42,'Use existing plants and customer approvals. Stage tooling against orders and cash conversion.'),(45,'Cap distributor inventory support. Test overseas service levels before granting exclusivity.'),(44,'₹1,000 crore of debt at 7.8% adds ₹78 crore of annual pretax interest.'),(43,'Asset or minority structures limit initial consideration. Underwrite quality and customer retention.'),(46,'A control premium must cover integration risk and satisfy promoter and minority shareholders.')]],ratios=[1.55,.73,4.2],size=13.2,emph=1)
    place(17,(base,table,stat,note,txt))
    place(18,(base,table,stat,note,txt))
    R.save(publish_path('output/CEAT_Investment_Banking_Pitch_Book.pptx'))
if __name__=='__main__':build()

