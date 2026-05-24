import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import ta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="TradeScanner Pro - Elite Setup", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stButton > button {
        width: 100%; background-color: #00ff88; color: black;
        font-weight: bold; border: none; padding: 15px; border-radius: 10px; font-size: 18px;
    }
    .stButton > button:hover { background-color: #00cc6a; }
    .elite-badge { background: linear-gradient(135deg, #ffd700, #ff8c00); color: black; 
        padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }
    .minervini-badge { background: #00ff88; color: black; padding: 3px 8px; border-radius: 5px; font-size: 11px; }
    .oneil-badge { background: #00aaff; color: white; padding: 3px 8px; border-radius: 5px; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("📊 TradeScanner Pro")
st.sidebar.markdown("### 🏆 Elite Trader Setup")
st.sidebar.info("""
**Kriterien der besten Trader:**
- Mark Minervini (SEPA)
- William O'Neil (CANSLIM)
- Stan Weinstein (Stage Analysis)
- Oliver Kell (Momentum)
""")

min_score = st.sidebar.slider("Min. Elite-Score:", 0, 100, 80)
st.sidebar.caption("80+ = Minervini-Qualität | 90+ = O'Neil-Meisterwerk")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Stage Analysis (Weinstein)")
stage_filter = st.sidebar.selectbox("Trend-Stage:", 
    ["Alle Stages", "Stage 2 (Aufwärtstrend)", "Stage 2+ (Starker Trend)", "Stage 4 (Abwärtstrend)"],
    index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Volumen & Liquidität")
min_volume = st.sidebar.number_input("Min. Tagesvolumen ($):", 0, 10000000000, 5000000, 1000000)
min_price = st.sidebar.number_input("Min. Preis ($):", 0.0, 100000.0, 15.0)
st.sidebar.caption("Minervini: Keine Aktien unter $15")

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Relative Stärke (RS)")
min_rs_rating = st.sidebar.slider("Min. RS-Rating:", 0, 100, 80)
st.sidebar.caption("O'Neil: Nur Aktien mit RS > 80")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Earnings & Wachstum")
min_eps_growth = st.sidebar.slider("Min. EPS-Wachstum (%):", 0, 500, 25)
min_rev_growth = st.sidebar.slider("Min. Umsatzwachstum (%):", 0, 500, 20)
st.sidebar.caption("CANSLIM: Starkes Gewinnwachstum")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Cache leeren"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("⚠️ Keine Finanzberatung!")
st.sidebar.caption("⏱ ~10-20 Min | Yahoo Finance")

# WAVETREND
def calc_wavetrend(df, ch1=10, ch2=21, ch3=34):
    try:
        hlc3 = (df['High'] + df['Low'] + df['Close']) / 3
        esa = hlc3.ewm(span=ch1, adjust=False).mean()
        d = abs(hlc3 - esa).ewm(span=ch1, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        wt1 = ci.ewm(span=ch2, adjust=False).mean()
        wt2 = wt1.rolling(window=ch3).mean()
        return wt1, wt2
    except:
        return pd.Series([np.nan]*len(df)), pd.Series([np.nan]*len(df))

# TICKER
@st.cache_data(ttl=86400)
def get_all_tickers():
    SP500 = ["A","AAL","AAPL","ABBV","ABNB","ABT","ACGL","ACN","ADBE","ADI","ADM","ADP","ADSK","AEE","AEP","AES","AFL","AIG","AIZ","AJG","AKAM","ALB","ALGN","ALK","ALL","ALLE","AMAT","AMCR","AMD","AME","AMGN","AMP","AMT","AMZN","ANET","ANSS","AON","AOS","APA","APD","APH","APTV","ARE","ATO","AVB","AVGO","AVY","AWK","AXP","AZO","BA","BAC","BALL","BAX","BBWI","BBY","BDX","BEN","BF.B","BG","BIIB","BIO","BK","BKNG","BKR","BLDR","BLK","BMY","BR","BRK.B","BRO","BSX","BWA","BXP","C","CAG","CAH","CARR","CAT","CB","CBOE","CBRE","CCI","CCL","CDNS","CDW","CE","CEG","CF","CFG","CHD","CHRW","CHTR","CI","CINF","CL","CLX","CMA","CMCSA","CME","CMG","CMI","CMS","CNC","CNP","COF","COO","COP","COR","COST","CPAY","CPB","CPRT","CPT","CRL","CRM","CSCO","CSGP","CSX","CTAS","CTLT","CTRA","CTSH","CTVA","CVS","CVX","CZR","D","DAL","DD","DE","DFS","DG","DGX","DHI","DHR","DIS","DLR","DLTR","DOV","DOW","DPZ","DRI","DTE","DUK","DVA","DVN","DXCM","EA","EBAY","ECL","ED","EFX","EIX","EL","ELV","EMN","EMR","ENPH","EOG","EPAM","EQIX","EQR","EQT","ES","ESS","ETN","ETR","ETSY","EVRG","EW","EXC","EXPD","EXPE","EXR","F","FANG","FAST","FCX","FDS","FDX","FE","FFIV","FICO","FIS","FITB","FMC","FOX","FOXA","FRT","FSLR","FTNT","FTV","GD","GE","GEHC","GEN","GILD","GIS","GL","GLW","GM","GNRC","GOOG","GOOGL","GPC","GPN","GRMN","GS","GWW","HAL","HAS","HBAN","HCA","HD","HES","HIG","HII","HLT","HOLX","HON","HPE","HPQ","HRL","HSIC","HST","HSY","HUBB","HUM","HWM","IBM","ICE","IDXX","IEX","IFF","ILMN","INCY","INTC","INTU","INVH","IP","IPG","IQV","IR","IRM","ISRG","IT","ITW","IVZ","J","JBHT","JBL","JCI","JKHY","JNJ","JNPR","JPM","K","KDP","KEY","KEYS","KHC","KIM","KLAC","KMB","KMI","KMX","KO","KR","KVUE","L","LDOS","LEN","LH","LHX","LIN","LKQ","LLY","LMT","LNC","LNT","LOW","LRCX","LULU","LUV","LVS","LW","LYB","LYV","MA","MAA","MAR","MAS","MCD","MCHP","MCK","MCO","MDLZ","MDT","MET","META","MGM","MHK","MKC","MLM","MMC","MMM","MNST","MO","MOH","MOS","MPC","MPWR","MRK","MRNA","MRO","MS","MSCI","MSFT","MSI","MTB","MTCH","MTD","MU","NCLH","NDAQ","NDSN","NEE","NEM","NFLX","NI","NKE","NOC","NOW","NRG","NSC","NTAP","NTRS","NUE","NVDA","NVR","NWL","NWS","NWSA","NXPI","O","ODFL","OKE","OMC","ON","ORCL","ORLY","OTIS","OXY","PANW","PARA","PAYC","PAYX","PCAR","PCG","PEG","PEP","PFE","PFG","PG","PGR","PH","PHM","PKG","PLD","PM","PNC","PNR","PNW","PODD","POOL","PPG","PPL","PRU","PSA","PSX","PTC","PWR","PYPL","QCOM","QRVO","RCL","REG","REGN","RF","RHI","RJF","RL","RMD","ROK","ROL","ROP","ROST","RSG","RTX","RVTY","SBAC","SBUX","SCHW","SHW","SJM","SLB","SMCI","SNA","SNPS","SO","SPG","SPGI","SRE","STE","STLD","STT","STX","STZ","SWK","SWKS","SYF","SYK","SYY","T","TAP","TDG","TDY","TECH","TEL","TER","TFC","TFX","TGT","TJX","TMO","TMUS","TPR","TRGP","TRMB","TROW","TRV","TSCO","TSLA","TSN","TT","TTWO","TXN","TXT","TYL","UA","UAL","UBER","UDR","UHS","ULTA","UNH","UNP","UPS","URI","USB","V","VFC","VICI","VLO","VLTO","VMC","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA","WBD","WDC","WEC","WELL","WFC","WHR","WM","WMB","WMT","WRB","WST","WTW","WY","WYNN","XEL","XOM","XRAY","XYL","YUM","ZBH","ZBRA","ZION","ZTS"]
    NASDAQ100 = ["AAPL","ABNB","ADBE","ADI","ADP","ADSK","AEP","AMAT","AMD","AMGN","AMZN","ANSS","ASML","AVGO","AZN","BIIB","BKNG","BKR","CDNS","CDW","CEG","CHTR","CMCSA","COST","CPRT","CRWD","CSCO","CSGP","CSX","CTAS","CTSH","DASH","DDOG","DLTR","DXCM","EA","EBAY","EXC","FANG","FAST","FTNT","GEHC","GFS","GILD","GOOG","GOOGL","HON","IDXX","ILMN","INTC","INTU","ISRG","JD","KDP","KHC","KLAC","LRCX","LULU","MAR","MCHP","MDB","MDLZ","MELI","META","MNST","MRNA","MRVL","MSFT","MU","NFLX","NVDA","NXPI","ODFL","ON","ORLY","PANW","PAYX","PCAR","PDD","PEP","PYPL","QCOM","REGN","ROP","ROST","SBUX","SGEN","SIRI","SNPS","SPLK","SWKS","TEAM","TMUS","TSLA","TXN","VRSK","VRTX","WBA","WBD","WDAY","XEL","ZS"]
    RUSSELL = ["AAON","AAN","AAWW","ABCB","ABG","ABM","ABR","ACAD","ACCD","ACCO","ACEL","ACHC","ACIW","ACLS","ACMR","ACRE","ACT","ACVA","ADMA","ADNT","ADUS","AEIS","AEO","AGIO","AGM","AGNC","AGX","AHCO","AHH","AIRS","AIT","AIZ","AJRD","AKR","AL","ALEX","ALG","ALGT","ALHC","ALIT","ALK","ALKS","ALLO","ALPN","ALRM","ALSN","ALTR","AM","AMBA","AMBC","AMCX","AMED","AMK","AMKR","AMN","AMPH","AMPY","AMR","AMRC","AMRX","AMSC","AMSF","AMSWA","AMTB","AMWD","AN","ANAB","ANDE","ANF","ANGO","ANIP","ANNX","AORT","AOSL","APAM","APG","APLE","APLS","APO","APOG","APPF","APPN","APPS","AR","ARAY","ARCB","ARCH","ARCO","ARDX","ARI","ARIS","ARLO","AROC","ARR","ARRY","ARTNA","ARVN","ARW","ARWR","ASAN","ASB","ASGN","ASH","ASIX","ASLE","ASO","ASPN","ASTE","ATEC","ATEN","ATEX","ATGE","ATKR","ATR","ATRC","ATRI","ATRO","ATSG","ATUS","AUB","AUPH","AUR","AVA","AVAV","AVD","AVDX","AVNS","AVNT","AVNW","AVO","AVT","AVXL","AWR","AX","AXGN","AXL","AXNX","AXON","AXSM","AZEK","AZTA","AZZ","B","BANC","BAND","BANF","BANR","BARK","BASE","BBSI","BC","BCC","BCO","BCPC","BDC","BE","BEAM","BECN","BERY","BFH","BFS","BGCP","BGS","BGSF","BH","BHB","BHE","BHF","BHLB","BIG","BIGC","BILL","BIO","BIPC","BIVI","BJRI","BKD","BKE","BKH","BKU","BL","BLBD","BLDR","BLFS","BLKB","BLMN","BLNK","BMBL","BMEA","BMI","BMRC","BMRN","BMY","BNL","BOC","BOH","BOOM","BOOT","BORR","BOX","BPOP","BRBR","BRC","BRCC","BRKL","BRP","BRSP","BRT","BRX","BRY","BSIG","BSRR","BSVN","BTBT","BTU","BUSE","BV","BWA","BWXT","BXMT","BXP","BY","BYD","BYON","BZH","CABA","CAC","CADE","CAKE","CAL","CALM","CALX","CAMP","CAPL","CARA","CARG","CARR","CARS","CASH","CASS","CATC","CATO","CATY","CBAN","CBB","CBRE","CBT","CBU","CBZ","CC","CCBG","CCCS","CCF","CCNE","CCO","CCOI","CCRN","CCS","CD","CDE","CDLX","CDNA","CDP","CDRE","CDXS","CE","CECO","CEIX","CENT","CENTA","CENX","CEPU","CERE","CERT","CFB","CFFN","CFR","CG","CGEM","CGTX","CHCO","CHCT","CHE","CHEF","CHGG","CHH","CHMG","CHRD","CHRS","CHRW","CHTR","CHUY","CHWY","CHX","CIEN","CIM","CINF","CIR","CIVI","CIX","CLAR","CLB","CLBK","CLDT","CLDX","CLF","CLFD","CLH","CLNE","CLOV","CLPR","CLR","CLS","CLSK","CLVT","CLW","CM","CMA","CMBM","CMC","CMCO","CME","CMP","CMPR","CMRE","CMRX","CMS","CNA","CNC","CNDT","CNK","CNM","CNMD","CNNE","CNO","CNOB","CNS","CNSL","CNTY","CNX","CNXC","CNXN","COCO","CODI","COFS","COGT","COHN","COHU","COKE","COLB","COLD","COLL","COMM","COMP","COOK","COOP","CORT","COUR","CPE","CPF","CPK","CPRX","CPSI","CPSS","CR","CRAI","CRBG","CRBK","CRC","CRDO","CRGE","CRGY","CRI","CRK","CRL","CRM","CRMT","CRNC","CRNX","CRS","CRSP","CRSR","CRVL","CRWD","CS","CSGS","CSR","CSTL","CSTM","CSV","CSWC","CTBI","CTGO","CTKB","CTLP","CTLT","CTO","CTOS","CTRA","CTRE","CTRN","CTS","CTSH","CUBI","CUE","CUZ","CVBF","CVCO","CVE","CVGI","CVGW","CVI","CVLG","CVLT","CVNA","CVRX","CVT","CW","CWAN","CWH","CWK","CWST","CXM","CXW","CYBR","CYH","CYT","CYTH","CYTK","CZFS","CZNC","CZR","D","DAKT","DAL","DAN","DAR","DAVA","DBD","DBI","DBRG","DCBO","DCGO","DCO","DCOM","DDD","DEA","DEI","DEN","DENN","DFH","DFIN","DFS","DGICA","DGII","DHC","DHIL","DIN","DIOD","DISH","DK","DKS","DLB","DLHC","DLR","DLTH","DLX","DM","DMRC","DNB","DNLI","DNOW","DNUT","DOC","DOCN","DOCS","DOLE","DOMO","DOOR","DORM","DOUG","DOV","DOX","DRH","DRI","DRQ","DRVN","DSGN","DSGR","DSKE","DSP","DT","DTE","DTM","DUK","DUNE","DUOL","DV","DVA","DVAX","DVN","DX","DXC","DXCM","DXPE","DY","DYN","EAF","EAT","EB","EBC","EBF","EBS","ECPG","ECVT","EDIT","EE","EEFT","EEX","EFC","EFSC","EGAN","EGBN","EGHT","EGLE","EGP","EGRX","EGY","EHAB","EHC","EIG","EJH","ELAN","ELF","ELVN","EMBC","EME","EML","EMN","ENFN","ENOV","ENR","ENS","ENSG","ENTA","ENTG","ENV","ENVA","ENVB","ENZ","EOLS","EP","EPAC","EPC","EPM","EPR","EPRT","EQBK","EQC","EQH","EQT","ERAS","ERII","ERJ","ERM","ESAB","ESCA","ESE","ESGR","ESI","ESNT","ESPR","ESQ","ESRT","ESS","ESTA","ESTC","ESTE","ET","ETD","ETNB","ETRN","ETSY","ETWO","EURN","EVA","EVC","EVCM","EVER","EVEX","EVGO","EVH","EVLV","EVO","EVOP","EVRI","EVTC","EW","EWBC","EWCZ","EWTX","EXAS","EXC","EXEL","EXFY","EXK","EXLS","EXPD","EXPE","EXPI","EXPO","EXR","EXTR","EYE","EYEN","EYPT","F","FA","FARO","FAST","FATE","FBK","FBMS","FBNC","FBP","FBRT","FC","FCBC","FCEL","FCF","FCFS","FCN","FCX","FDP","FDUS","FE","FELE","FENC","FER","FF","FFBC","FFIC","FFIN","FFIV","FFWM","FG","FGBI","FHB","FHI","FHL","FHTX","FI","FIBK","FICO","FIGS","FINW","FIP","FIS","FISI","FITB","FIVE","FIVN","FIX","FIZZ","FL","FLGT","FLIC","FLL","FLNC","FLNG","FLR","FLS","FLT","FLWS","FLYW","FMAO","FMBH","FMC","FMNB","FMS","FMTX","FN","FNA","FNB","FND","FNF","FNKO","FNLC","FNV","FNWB","FOCS","FOLD","FOR","FORA","FORD","FORM","FORR","FOSL","FOUR","FOX","FOXA","FOXF","FPI","FR","FRA","FRAF","FRBA","FRBK","FRC","FREE","FREQ","FRG","FRGE","FRGI","FRHC","FROG","FRPH","FRPT","FRSH","FRST","FRSX","FRT","FSBC","FSBW","FSEA","FSFG","FSK","FSLR","FSM","FSP","FSS","FSTR","FT","FTAI","FTC","FTCI","FTDR","FTEK","FTFT","FTHM","FTK","FTNT","FTRE","FTS","FTV","FUBO","FUL","FULT","FUN","FUNC","FUSN","FUTU","FVCB","FVRR","FWONA","FWRD","FWRG","FXNC"]
    DAX40 = ["ADS.DE","AIR.DE","ALV.DE","BAS.DE","BAYN.DE","BMW.DE","BNR.DE","CBK.DE","CON.DE","DTE.DE","DBK.DE","DB1.DE","DPW.DE","DRW3.DE","EOAN.DE","FRE.DE","FME.DE","HEI.DE","HEN3.DE","IFX.DE","LIN.DE","MBG.DE","MRK.DE","MTX.DE","MUV2.DE","PAH3.DE","PUM.DE","QIA.DE","RWE.DE","SAP.DE","SIE.DE","SRT3.DE","VOW3.DE","VNA.DE","ZAL.DE","SY1.DE","HFG.DE","SHL.DE","BOSS.DE","EVT.DE"]
    
    all_tickers = SP500.copy()
    for t in NASDAQ100:
        if t not in all_tickers: all_tickers.append(t)
    for t in RUSSELL:
        if t not in all_tickers: all_tickers.append(t)
    for t in DAX40:
        if t not in all_tickers: all_tickers.append(t)
    return all_tickers
