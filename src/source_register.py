"""Write provenance, including the dated exchange file behind every price observation."""
import csv
from data_collection import ROOT,RAW,DOCS,NSE,BASE
def write_sources():
    rows=[]
    def add(key,issuer,title,url,date,period,items,proof='Dated primary document; period and scope checked'):
        rows.append([key,issuer,title,url,date,period,items,'2026-11-08',proof])
    for y,date,period,pages in [('22','2022 (exact dispatch day unverified)','FY21 opening','114'),('23','2023 (exact dispatch day unverified)','FY22–23','126–127'),('24','2024 (exact dispatch day unverified)','FY24','122–123'),('26','2026-07-23','FY25–26','138–139, notes 17, 20, 28 and geographical disclosures')]:
        key='AR'+y; url=DOCS.get(key+'.pdf',BASE+'CEAT%20AR%202021-22_Spread-27.6.22.pdf')
        add(key,'CEAT','Integrated annual report FY'+y,url,date,period,'Consolidated statements; PDF pages '+pages)
    for k,name,title,date,stuff in [('H1','H1FY27','October board outcome','2026-10-14','Consolidated statements, PDF pp16–18'),('MIX','H1presentation','Q2 investor presentation','2026-10-14','Group performance; standalone shares on p7'),('CALL','H1transcript','Q2 earnings call','2026-10-15 (call date)','Management commentary on costs, capacity, CAMSO and capex')]:
        add(k,'CEAT',title,DOCS[name+'.pdf'],date,'Q2/H1 FY27',stuff)
    add('SHP','CEAT','Shareholding pattern',BASE+'shpfinal.pdf','October quarter filing; issuer PDF generated 2026-11-03','Sep 2026','Table I: issued shares, promoter, public and employee trust')
    for k,date,period in [('JK26','2026-05-26','FY26'),('MRF26','2026-05-07','FY26'),('APOLLO26','2026-05-14','FY26'),('APOLLOH127','2026-11-04','H1 FY27'),('JKH127','2026-10-23','H1 FY27'),('APOLLOH126','2025-11-13','H1 FY26')]:
        u=DOCS.get(k+'.html',NSE+'corporate/ixbrl/INTEGRATED_FILING_INDAS_127406_13112025184923_iXBRL_WEB.html')
        add(k,'Issuer via NSE','Consolidated Ind AS integrated filing',u,date,period,'Income, balance sheet; displayed lakhs divided by 100')
    for k,company,title,u,date,items in [
        ('JKH1report','JK Tyre','Interim consolidated statements','https://dwzytf8fljslz.cloudfront.net/CFS_SEP_2026_a7649b575d.pdf','2026-10-23','pp4,6 restated H1 comparable and leases'),
        ('JKFYreport','JK Tyre','Annual consolidated results','https://dwzytf8fljslz.cloudfront.net/CFS_Mar_2026_101522c61b.pdf','2026-05-26','p7 restated FY25 comparative'),
        ('JKSH','JK Tyre','September ownership','https://dwzytf8fljslz.cloudfront.net/SH_Pwebsite_bfd9688559.pdf','2026-10-21 (document date)','28,82,89,511 issued shares'),
        ('APSH','Apollo Tyres','September ownership','https://corporate.apollotyres.com/content/dam/orbit/apollo-corporate/investors/shareholding-information/shareholding-pattern/2026-27/Shareholding%20Pattern%20-%20September%2030,%202026.pdf','2026-10-21','635,100,946 issued shares'),
        ('APFY','Apollo Tyres','Full-year results','https://corporate.apollotyres.com/press-and-media/news/financial/q4-fy26/','2026-05-14','FY25 comparator and FY26 special items'),
        ('MRFAR','MRF','Annual report 2025–26','https://www.mrftyres.com/downloads/Annual%20Report%20-%20Final%2013.7.2026.pdf','July 2026','Consolidated pp145–146 printed; shares, leases, liquid deposits and parent earnings'),
        ('YIELD','CCIL','Tenor-wise indicative yields','https://dr.ccilindia.com/web/ccil/tenorwise-indicative-yields','2026-11-06','6.94% GS 2036, 9–10Y bucket, 7.1816%'),
        ('ERP','Aswath Damodaran, NYU','Country risk premium spreadsheet, July edition','https://pages.stern.nyu.edu/~adamodar/pc/datasets/ctrypremJuly26.xlsx','2026-07-15 (release article)','India row 73 D/E, rating-based default spread and total ERP'),
        ('SIAM','SIAM','FY26 automobile industry performance','https://www.siam.in/pressrelease-details.aspx?mpgid=48&pgidtrail=50&pid=605','2026-04-14','FY26 wholesale volume and growth'),
        ('ICRA','ICRA','Rising raw material costs to weigh on tyre industry profitability','https://www.icra.in/Research/ViewResearchReport/rising-raw-material-costs-to-weigh-on-tyre-industry-profitability-in-fy2027/7142','2026-09-30','Q1 sample growth; FY27 domestic demand and margin forecast'),
        ('EXPORT','India Brand Equity Foundation','Tyre exports reach record US$3.09bn','https://www.ibef.org/news/tyre-exports-reach-record-us-3-09-billion-in-fy26-despite-supply-chain-disruptions','2026-06-04','FY25 and FY26 export values; ATMA data'),
    ]: add(k,company,title,u,date,'See title / data field',items)
    add('MRFJune','MRF via NSE','June consolidated interim results','https://nsearchives.nseindia.com/corporate/MRF_11082026122306_RESULTAUGUST.pdf','2026-08-11','Q1 FY27 and FY26 comparative','p8; separate June LTM cross-check')
    add('ATMA','ATMA','Indian tyre industry overview','https://www.atmaindia.org.in/an-overview/','Exact day unavailable; overview also in Kochi press release indexed by Oct 2026','FY25 estimate','Industry turnover around INR 100,000 crore; estimated, not audited')
    add('TVS','TVS Srichakra','Annual report 2025–26','https://www.eurogriptyres.com/investor-relations/annual-report','September 2026','FY26','Two-wheeler and off-highway capacities and Madurai expansion')
    add('INDAG','Indag Rubber','Annual report 2025–26','https://indagrubber.com/investors/annual-reports-other-reports','July 2026','FY26','Pre-cured tread, bonding materials and retreading')
    with (RAW/'market.csv').open() as f:
        prices={r['date']:r['source'] for r in csv.DictReader(f)}
    for date,u in prices.items():add('NSE '+date,'NSE','Daily cash-market security-wise delivery and price file',u,date,date,'EQ CLOSE_PRICE; weekly price panel and valuation cross-section')
    with (ROOT/'data/sources.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['ID','Source','Document','Original URL','Publication date / evidence','Period','Data retrieved','Retrieved','Verification']);w.writerows(rows)
    return rows

