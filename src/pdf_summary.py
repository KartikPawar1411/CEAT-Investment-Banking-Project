"""One-page valuation brief, generated from the saved Excel model."""
from committee import *
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
def build():
    regular=os.environ.get('CEAT_FONT_REGULAR','C:/Windows/Fonts/calibri.ttf')
    bold=os.environ.get('CEAT_FONT_BOLD','C:/Windows/Fonts/calibrib.ttf')
    pdfmetrics.registerFont(TTFont('Body',regular));pdfmetrics.registerFont(TTFont('Bold',bold))
    navy='#15354A';teal='#167D76';grey='#526A76';pale='#E9F1F2';white='#FFFFFF'
    c=canvas.Canvas(str(publish_path('output/CEAT_Valuation_Summary.pdf')),pagesize=A4)
    W,H=A4;c.setTitle('CEAT Limited | Valuation summary | 6 November 2026');c.setAuthor('Independent academic simulation')
    def txt(x,y,t,size=11,font='Body',color=navy):c.setFont(font,size);c.setFillColor(HexColor(color));c.drawString(x,H-y,t)
    def rect(x,y,w,h,color):c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)
    def lines(x,y,t,width,size=11.4,leading=15,color=grey):
        current=''
        for word in t.split():
            trial=(current+' '+word).strip()
            if pdfmetrics.stringWidth(trial,'Body',size)>width and current:
                txt(x,y,current,size,'Body',color);y+=leading;current=word
            else:current=trial
        if current:txt(x,y,current,size,'Body',color)
        return y+leading
    rect(0,0,W,115,navy);txt(34,33,'CEAT LIMITED   /   INVESTMENT COMMITTEE',10,'Bold','#9AD1C7')
    txt(33,73,'Funding the next capacity tranche',26,'Bold',white)
    txt(35,96,'6 November 2026   |   Consolidated   |   INR crore unless indicated',11,'Body','#CCDFE0')
    txt(34,146,outcome(),15,'Bold',teal)
    lines(34,168,gate(),526,12,15)
    for x,label,value in [(34,'SELF-FUNDED ON TIME',cv(F,'G4')),(216,'PROPOSED TRANCHE',cv(FI,'B5')),(395,'PEAK BASE BRIDGE',cv(F,'C4'))]:
        txt(x,225,label,9,'Bold',teal);txt(x,251,value,22,'Bold')
    txt(34,290,'Liquidity through March 2028',17,'Bold')
    xx=[39,145,220,310,401,484];headers=['Case','First gap','Peak bridge','Pre-bridge low','Funded low','Affordable']
    rect(34,306,527,25,navy)
    for x,h in zip(xx,headers):txt(x,322,h,9,'Bold',white)
    for i,row in enumerate(funding_table()):
        y=331+i*22;rect(34,y,527,22,pale if i%2==0 else white)
        for x,val in zip(xx,[row[j] for j in [0,1,2,4,5,6]]):txt(x,y+15,val,10)
    lines(34,458,external()+' The bridge assumes access to credit. Negative cash measures the unfinanced deficit.',524,10.4,13)
    txt(34,513,'Valuation and the operating hurdle',17,'Bold')
    lines(34,534,dcf_story()+f' FY26 peer EV/EBITDA implies {price(v(VS,"B6"))}–{price(v(VS,"D6"))}.',524,11,14)
    lines(34,594,f'The original {price(v(ND,"B48"))} DCF required {cv(ND,"B50")} of FY31-equivalent cash flow against {cv(ND,"B49")} modeled. The upgraded market-clearing case requires a {percent(ND,"B42")} FY31 EBITDA margin, allowing for growth reinvestment.',524,10.8,14)
    txt(34,669,'Release conditions',13,'Bold',teal)
    lines(34,687,f'Confirm rollover and firm funding. Delay orders if any quarter misses the {cv(FI,"B4")} floor. Re-test recovery if basket inflation exceeds the 3–3.5% Q3 outlook. Reserve the separate US$44m trademark payment in Q2 FY29.',524,10.7,13)
    rect(34,744,527,1,'#C8D6D8')
    lines(34,763,'Sources: CEAT FY26 notes 20, 42 and 52; Oct 14 H1 results pp16–20; Oct 15 call pp3–4, 13–14; NSE close, peer filings, CCIL and July ERP. The tranche, cash floor and financing terms are analyst assumptions.',524,9.2,11)
    txt(34,817,'Independent public-information analysis',9,'Body',grey)
    c.save()
if __name__=='__main__':build()

