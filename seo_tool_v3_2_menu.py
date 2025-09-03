"""
SEO Automation Tool v3.5 - Selenium Default + SPA/React Ready
"""

import sys, threading, io
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from collections import Counter
import nltk
nltk.download('punkt')
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal, QObject
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt

# ---------------- Signals ----------------
class Signals(QObject):
    log_signal = pyqtSignal(str)
    chart_signal = pyqtSignal(object)

# ---------------- Selenium Fetch ----------------
def fetch_html_selenium(url, log_func=print):
    try:
        log_func("Checking ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        log_func(f"ChromeDriver at: {driver_path}")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        log_func(f"Opening URL: {url}")
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        html = driver.page_source
        driver.quit()
        log_func("Selenium fetch successful.")
        return html
    except Exception as e:
        log_func(f"[Selenium Error] {e}")
        return None

# ---------------- Parse & Analyze ----------------
def parse_html(html, base_url=""):
    soup = BeautifulSoup(html,"html.parser")
    title = soup.title.string.strip() if soup.title else ""
    metas = {meta.get("name",""):meta.get("content","") for meta in soup.find_all("meta") if meta.get("name")}
    headings = {f"h{i}":[h.get_text().strip() for h in soup.find_all(f"h{i}")] for i in range(1,7)}
    body_text = soup.get_text(separator=" ", strip=True)
    links = [urljoin(base_url, a.get("href")) for a in soup.find_all("a", href=True)]
    alts = [img.get("alt","") for img in soup.find_all("img")]
    return {"title":title, "metas":metas, "headings":headings, "body":body_text, "links":links, "alts":alts}

def keyword_density(text):
    words = nltk.word_tokenize(text.lower())
    words = [w for w in words if w.isalpha()]
    count = Counter(words)
    total = sum(count.values())
    if total==0: return {}
    return {k: round(v/total*100,2) for k,v in count.items()}

def analyze_page(parsed):
    report = {}
    report["Title"] = parsed["title"]
    report["Meta Description"] = parsed["metas"].get("description","")
    for i in range(1,7):
        report[f"H{i} Count"] = len(parsed["headings"].get(f"h{i}",[]))
    report["Internal Links"] = len([l for l in parsed["links"] if urlparse(l).netloc==""])
    report["External Links"] = len([l for l in parsed["links"] if urlparse(l).netloc!=""])
    full_text = parsed["body"] + " " + parsed["title"] + " " + report["Meta Description"] + " " + " ".join(parsed["alts"])
    report["Keyword Density"] = keyword_density(full_text)
    report["Top Keywords"] = dict(sorted(report["Keyword Density"].items(), key=lambda x:x[1], reverse=True)[:10])
    return report

def check_broken_links(links):
    seen=set()
    broken=[]
    for l in links:
        if not l or l in seen: continue
        seen.add(l)
        try:
            r=requests.head(l,timeout=5, allow_redirects=True)
            if r.status_code>=400:
                broken.append((l,r.status_code))
        except:
            broken.append((l,"error"))
    return broken

# ---------------- Export ----------------
def export_excel(report_list, filename="seo_report.xlsx"):
    df_list=[]
    for r in report_list:
        temp=r.copy()
        temp.update({"Top Keywords":", ".join([f"{k}:{v}%" for k,v in r.get("Top Keywords",{}).items()])})
        temp["Broken Links"]=", ".join([f"{l}({s})" for l,s in r.get("Broken Links",[])])
        df_list.append(temp)
    df=pd.DataFrame(df_list)
    df.to_excel(filename,index=False)

def export_pdf(report_list, filename="seo_report.pdf"):
    c=canvas.Canvas(filename,pagesize=letter)
    width,height=letter
    y=height-40
    for r in report_list:
        c.setFont("Helvetica-Bold",12)
        c.drawString(30,y,f"Title: {r['Title']}")
        y-=20
        c.setFont("Helvetica",10)
        c.drawString(30,y,f"Meta Description: {r['Meta Description']}")
        y-=20
        c.drawString(30,y,f"H1:{r['H1 Count']} H2:{r['H2 Count']} H3:{r['H3 Count']}")
        y-=15
        c.drawString(30,y,f"Internal:{r['Internal Links']} External:{r['External Links']}")
        y-=15
        c.drawString(30,y,f"Top Keywords: {', '.join([f'{k}:{v}%' for k,v in r.get('Top Keywords',{}).items()])}")
        y-=15
        c.drawString(30,y,f"Broken Links: {len(r.get('Broken Links',[]))}")
        y-=20
        if "Chart Image" in r:
            img=ImageReader(io.BytesIO(r["Chart Image"]))
            c.drawImage(img,30,y-200,width=500,height=200)
            y-=220
        y-=20
        if y<100:
            c.showPage()
            y=height-40
    c.save()

def plot_chart_figure(report):
    fig=Figure(figsize=(6,3))
    ax=fig.add_subplot(111)
    headings=[report.get(f"H{i} Count",0) for i in range(1,4)]
    ax.bar(["H1","H2","H3"],headings,color='skyblue')
    top_kw=report.get("Top Keywords",{})
    ax2=ax.twinx()
    ax2.plot(list(top_kw.keys()),list(top_kw.values()),color='red',marker='o')
    ax.set_ylabel("Heading Count")
    ax2.set_ylabel("Keyword Density (%)")
    ax.set_title("SEO Analysis Chart")
    fig.tight_layout()
    buf=io.BytesIO()
    fig.savefig(buf,format="png")
    buf.seek(0)
    return buf.read(), fig

# ---------------- GUI ----------------
class SEOToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEO Automation Tool v3.5")
        self.setGeometry(50,50,1200,700)
        self.signals=Signals()
        self.signals.log_signal.connect(self.append_log)
        self.signals.chart_signal.connect(self.update_chart)

        self.url_input=QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        self.file_button=QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        self.run_button=QPushButton("Run SEO Audit")
        self.run_button.clicked.connect(self.run_threaded_audit)

        self.output_area=QTextEdit()
        self.output_area.setReadOnly(True)
        self.figure=Figure(figsize=(6,3))
        self.canvas=FigureCanvas(self.figure)

        top_layout=QHBoxLayout()
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(self.file_button)
        top_layout.addWidget(self.run_button)

        layout=QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.output_area)
        layout.addWidget(self.canvas)

        container=QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.file_path=None

    def append_log(self,msg):
        self.output_area.append(msg)

    def update_chart(self,fig):
        self.canvas.figure.clear()
        ax=self.canvas.figure.add_subplot(111)
        for a in fig.axes:
            for line in a.get_lines():
                ax.plot(line.get_xdata(),line.get_ydata(),color=line.get_color(),marker='o')
            for bar in a.patches:
                ax.bar(bar.get_x(),bar.get_height(),color=bar.get_facecolor())
        self.canvas.draw()

    def select_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Select URL file","","Text Files (*.txt)")
        if path:
            self.file_path=path
            self.signals.log_signal.emit(f"Selected file: {path}")

    def run_threaded_audit(self):
        t=threading.Thread(target=self.run_audit)
        t.start()

    def run_audit(self):
        urls=[]
        if self.file_path:
            with open(self.file_path,"r") as f:
                urls=[line.strip() for line in f if line.strip()]
        elif self.url_input.text().strip():
            urls=[self.url_input.text().strip()]
        else:
            self.signals.log_signal.emit("No URL provided.")
            return

        all_reports=[]
        for url in urls:
            self.signals.log_signal.emit(f"Processing {url} ...")
            html=fetch_html_selenium(url, log_func=self.signals.log_signal.emit)
            if not html:
                self.signals.log_signal.emit(f"Failed to fetch {url}")
                continue
            parsed=parse_html(html, base_url=url)
            report=analyze_page(parsed)
            report["Broken Links"]=check_broken_links(parsed["links"])
            chart_img, fig=plot_chart_figure(report)
            report["Chart Image"]=chart_img
            self.signals.chart_signal.emit(fig)
            all_reports.append(report)
            self.signals.log_signal.emit(f"Report for {url}: {report}")

        if all_reports:
            export_excel(all_reports)
            export_pdf(all_reports)
            self.signals.log_signal.emit("Exported Excel & PDF.")

# ---------------- Main ----------------
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=SEOToolGUI()
    window.show()
    sys.exit(app.exec_())
