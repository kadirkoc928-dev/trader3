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

st.set_page_config(page_title="TradeScanner Pro", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stButton > button {
        width: 100%; background-color: #00ff88; color: black;
        font-weight: bold; border: none; padding: 15px; border-radius: 10px; font-size: 18px;
    }
    .stButton > button:hover { background-color: #00cc6a; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("📊 TradeScanner Pro")
st.sidebar.info("S&P 500 + NASDAQ 100 + Russell 2000 + DAX 40\n\nALLE Aktien + Wavetrend")

min_score = st.sidebar.slider("Min. Swing-Score:", 0, 100, 75)
min_volume = st.sidebar.number_input("Min. Volumen ($):", 0, 10000000000, 1000000, 500000)
min_price = st.sidebar.number_input("Min. Preis ($):", 0.0, 100000.0, 5.0)
max_price = st.sidebar.number_input("Max. Preis ($):", 0.0, 100000.0, 1000.0)
rsi_min = st.sidebar.slider("RSI Min:", 0, 100, 35)
rsi_max = st.sidebar.slider("RSI Max:", 0, 100, 70)
adx_min = st.sidebar.slider("ADX Min:", 0, 100, 20)
vol_ratio_min = st.sidebar.slider("Vol Ratio Min:", 0.5, 5.0, 1.0)

if st.sidebar.button("🗑️ Cache leeren"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("⚠️ Keine Finanzberatung!")

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

# INDIKATOREN
def calc_indicators(df):
    if len(df) < 30: return None
    try:
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'], window=14)
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_hist'] = ta.trend.macd_diff(df['Close'])
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        df['WT1'], df['WT2'] = calc_wavetrend(df)
        return df
    except:
        return None

def swing_score(df):
    if df is None or len(df) < 30: return 0
    try:
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        score = 0
        if pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
            if latest['SMA_20'] > latest['SMA_50']: score += 15
            if latest['Close'] > latest['SMA_20']:
                score += 10
                d = (latest['Close'] - latest['SMA_20']) / latest['SMA_20'] * 100
                if 0 < d < 3: score += 5
        if pd.notna(latest.get('ADX')):
            adx = latest['ADX']
            if adx > 50: score += 25
            elif adx > 40: score += 22
            elif adx > 35: score += 18
            elif adx > 30: score += 15
            elif adx > 25: score += 10
            elif adx > 20: score += 5
            else: score += 1
        if pd.notna(latest.get('RSI')):
            rsi = latest['RSI']
            rsi_prev = prev.get('RSI', rsi)
            if 45 <= rsi <= 58: score += 20
            elif 40 <= rsi <= 65: score += 16
            elif 35 <= rsi <= 70: score += 10
            elif rsi < 35: score += 6
            elif rsi > 70: score += 4
            else: score += 2
            if pd.notna(rsi_prev) and rsi > rsi_prev: score += 2
        if pd.notna(latest.get('Volume_Ratio')):
            vr = latest['Volume_Ratio']
            if 1.3 <= vr <= 2.5: score += 15
            elif 1.1 <= vr <= 3.0: score += 12
            elif 0.9 <= vr <= 3.5: score += 8
            elif vr > 0.7: score += 4
            else: score += 1
        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_signal')):
            if latest['MACD'] > latest['MACD_signal'] and latest['MACD'] > 0: score += 7
            elif latest['MACD'] > latest['MACD_signal']: score += 5
            elif latest['MACD'] > 0: score += 3
            mh = latest.get('MACD_hist', 0)
            ph = prev.get('MACD_hist', 0)
            if pd.notna(mh) and pd.notna(ph) and mh > ph: score += 3
        if pd.notna(latest.get('WT1')) and pd.notna(latest.get('WT2')):
            if latest['WT1'] > latest['WT2']: score += 5
            if latest['WT1'] < -50: score += 3
        return min(100, score)
    except:
        return 0

def tv_link(ticker):
    u = ticker.upper()
    if '.DE' in u: e, c = "XETR", u.replace('.DE','')
    else: e, c = "NASDAQ", u
    return f"https://www.tradingview.com/chart/?symbol={e}%3A{c}&interval=D"

def wt_signal(wt1, wt2):
    if pd.isna(wt1) or pd.isna(wt2): return "N/A", "gray"
    if wt1 > wt2:
        if wt1 < -50: return "Bullish (OS)", "#00ff88"
        elif wt1 > 50: return "Bullish (OB)", "#88ff00"
        else: return "Bullish", "#44ff00"
    else:
        if wt1 > 50: return "Bearish (OB)", "#ff4444"
        elif wt1 < -50: return "Bearish (OS)", "#ff8800"
        else: return "Bearish", "#ff0000"

def scan_one(ticker):
    try:
        s = yf.Ticker(ticker)
        df = s.history(period="3mo", interval="1d")
        if df.empty or len(df) < 30: return None
        avg_v = df['Volume'].tail(20).mean()
        price = df['Close'].iloc[-1]
        dv = avg_v * price
        if dv < 500000: return None
        df = calc_indicators(df)
        if df is None: return None
        score = swing_score(df)
        latest = df.iloc[-1]
        try:
            name = s.info.get('shortName', ticker)
            if name is None: name = ticker
        except:
            name = ticker
        rsi_v = latest.get('RSI', 50)
        if pd.isna(rsi_v): rsi_v = 50
        adx_v = latest.get('ADX', 20)
        if pd.isna(adx_v): adx_v = 20
        vr_v = latest.get('Volume_Ratio', 1.0)
        if pd.isna(vr_v): vr_v = 1.0
        atr_v = latest.get('ATR', 0)
        if pd.isna(atr_v) or price == 0: atr_p = 2.0
        else: atr_p = (atr_v / price) * 100
        sma_v = latest.get('SMA_20')
        if pd.isna(sma_v): sma_s = 'N/A'
        else: sma_s = 'Above' if price > sma_v else 'Below'
        macd = latest.get('MACD')
        macd_s = latest.get('MACD_signal')
        if pd.isna(macd) or pd.isna(macd_s): macd_st = 'N/A'
        else: macd_st = 'Bullish' if macd > macd_s else 'Bearish'
        wt1_v = latest.get('WT1', np.nan)
        wt2_v = latest.get('WT2', np.nan)
        wts, wtc = wt_signal(wt1_v, wt2_v)
        return {
            'Ticker': ticker, 'Name': str(name)[:50], 'Preis': round(price, 2),
            'Swing-Score': score, 'RSI': round(rsi_v, 1), 'ADX': round(adx_v, 1),
            'Vol Ratio': round(vr_v, 2), 'ATR%': round(atr_p, 2),
            'SMA20': sma_s, 'MACD': macd_st,
            'Wavetrend': wts, 'WT_Color': wtc,
            'Volumen': round(dv, 0), 'Chart': tv_link(ticker)
        }
    except:
        return None

# MAIN
st.title("🎯 S&P 500 + NASDAQ 100 + Russell 2000 + DAX 40")
st.markdown("### ALLE Aktien + Wavetrend-Indikator")

all_tickers = get_all_tickers()
st.success(f"✅ **{len(all_tickers):,} Ticker geladen**")

if st.button("🚀 ALLE AKTIEN SCANNEN", type="primary", use_container_width=True):
    st.markdown("---")
    progress_bar = st.progress(0)
    status_text = st.empty()
    time_text = st.empty()
    
    results = []
    total = len(all_tickers)
    completed = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(scan_one, t): t for t in all_tickers}
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            if result is not None: results.append(result)
            if completed % 100 == 0 or completed == total:
                progress_bar.progress(completed / total)
                elapsed = time.time() - start_time
                speed = completed / elapsed if elapsed > 0 else 0
                remaining = (total - completed) / speed if speed > 0 else 0
                status_text.text(f"✅ {completed:,}/{total:,} | 🎯 {len(results):,} Treffer")
                time_text.text(f"⏱ {elapsed:.0f}s | ⏳ ~{remaining:.0f}s")
    
    progress_bar.empty()
    status_text.empty()
    time_text.empty()
    total_time = time.time() - start_time
    
    if results:
        df_all = pd.DataFrame(results)
        df_filtered = df_all[(df_all['Swing-Score']>=min_score)&(df_all['Volumen']>=min_volume)&(df_all['Preis']>=min_price)&(df_all['Preis']<=max_price)&(df_all['RSI']>=rsi_min)&(df_all['RSI']<=rsi_max)&(df_all['ADX']>=adx_min)&(df_all['Vol Ratio']>=vol_ratio_min)]
        df_filtered = df_filtered.sort_values('Swing-Score', ascending=False)
        
        st.markdown("---")
        st.subheader(f"🎯 {len(df_filtered):,} Aktien mit Score ≥{min_score}")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📊 Treffer", len(df_filtered))
        with c2: st.metric("⏱ Zeit", f"{total_time:.0f}s ({total_time/60:.1f} Min)")
        with c3:
            best = df_filtered['Swing-Score'].max() if not df_filtered.empty else 0
            st.metric("🏆 Bester", f"{best}/100")
        
        if not df_filtered.empty:
            for i, (_, row) in enumerate(df_filtered.iterrows()):
                score = row['Swing-Score']
                if score >= 90: emoji, color = "🌟", "#00ff88"
                elif score >= 85: emoji, color = "✅", "#88ff00"
                elif score >= 80: emoji, color = "👍", "#44ff00"
                else: emoji, color = "📊", "#ffaa00"
                
                col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.5, 1.2, 0.7, 0.6, 0.6, 0.6, 1.0, 0.7, 0.7])
                col1.markdown(f"<span style='color:{color};font-weight:bold'>{emoji} {score}</span>", unsafe_allow_html=True)
                col2.markdown(f"**{row['Ticker']}**\n*{row['Name'][:30]}*")
                col3.markdown(f"${row['Preis']:.2f}")
                col4.markdown(f"RSI {row['RSI']:.1f}")
                col5.markdown(f"ADX {row['ADX']:.1f}")
                col6.markdown(f"Vol {row['Vol Ratio']:.1f}x")
                col7.markdown(f"<span style='color:{row['WT_Color']};font-size:12px'>{row['Wavetrend']}</span>", unsafe_allow_html=True)
                col8.markdown(f"<span style='color:{'#00ff88' if row['MACD']=='Bullish' else '#ff4444'}'>{row['MACD']}</span>", unsafe_allow_html=True)
                col9.markdown(f"[📈 Chart]({row['Chart']})")
               csv = df_filtered.to_csv(index=False)
            st.download_button(f"📥 {len(df_filtered)} Ergebnisse als CSV", csv, f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 'text/csv')
            
            st.markdown("---")
            st.subheader("🏆 Top 10 Details")
            top10 = df_filtered.head(10)
            for i, (_, row) in enumerate(top10.iterrows()):
                with st.expander(f"#{i+1} {row['Ticker']} | Score: {row['Swing-Score']}/100 | ${row['Preis']:.2f}", expanded=(i<3)):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Score", f"{row['Swing-Score']}/100")
                        st.metric("Preis", f"${row['Preis']:.2f}")
                    with c2:
                        st.metric("RSI", f"{row['RSI']:.1f}")
                        st.metric("ADX", f"{row['ADX']:.1f}")
                    with c3:
                        st.metric("ATR%", f"{row['ATR%']:.2f}%")
                        st.metric("Vol Ratio", f"{row['Vol Ratio']:.2f}x")
                    with c4:
                        st.metric("SMA20", row['SMA20'])
                        st.metric("MACD", row['MACD'])
                    st.markdown(f"🌊 **Wavetrend:** {row['Wavetrend']}")
                    st.markdown(f"[📈 TradingView 1-Tages-Chart]({row['Chart']})")
        else:
            st.warning(f"⚠️ Keine Aktien mit Score ≥{min_score}. Filter lockern!")
    else:
        st.error("❌ Keine Ergebnisse! Cache leeren & neu versuchen.")

st.markdown("---")
st.caption(f"⚠️ Keine Finanzberatung | Yahoo Finance (verzögert) | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
