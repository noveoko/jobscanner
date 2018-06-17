from bs4 import BeautifulSoup as bs
import re, time, requests, random, re
from pathlib import Path
import os

def collect_jobs():
with open('uw_madison_jobs.html') as infile:
    with open('jobs_to_check.txt','w') as outfile:
        jobs = {}
        soup = bs(infile.read(), 'html.parser')
        links = soup.find_all('a')
        for link in links:
            if link.text.isupper():
                job_title = link.text
                job_link = link['href']
                full_url = 'http://jobs.hr.wisc.edu' + job_link
                outfile.write(f"{job_title}\t{full_url}\n")

def get_page(url):
    request = requests.get(url)
    if request.status_code == 200:
        return request.content
    else:
        print(request.status_code)

def app():
    with open('jobs_to_check.txt') as infile:
        data = infile.readlines()
        for line in data:
            title, url = line.split('\t')
            if title.isupper():
                print(title)
                url = url.strip()
                if re.match("(http://jobs.hr.wisc.edu/cw/en-us/job/[0-9]{2,20}/[a-z\-]+)",url):
                    print(url)
                    file_to_check = Path(f"job_pages_html/{title}.html")
                    if not file_to_check.is_file():
                        page = get_page(url)
                        time.sleep(random.choice(range(4,20)))
                        if page:
                            try:
                                with open(f'job_pages_html/{title}.html','w') as outfile:
                                    outfile.write(str(page))
                            except FileNotFoundError as fe:
                                print(fe)
                    else:
                        print('url not valid')
            
def process_job_posts(path='job_pages_html'):
    pattern = re.compile(r"(.?)*(\$[0-9\,]+)")
    all_jobs = []
    dirc = os.fsencode('job_pages_html')
    for file in os.listdir(dirc):
        fname = os.fsdecode(file)
        if fname.endswith(".html"):
            file_path = f"{path}/{fname}"
            raw_html = open(file_path,'r').read()
            soup = bs(raw_html, 'html.parser')
            rows = soup.find_all('tr')
            result = []
            for row in rows:
                heading = row.find('th')
                if heading and 'Advertised Salary' in heading.text:
                    #print(heading.text.strip())
                    section = row.find('td')
                    if section:
                        try:
                            m = re.match(pattern, row.text)
                            data_line = f"{m.group(2).strip()}"
                            result.append(data_line)
                        except Exception:
                            result.append('No salary provided')
                            #print(ee)
                    else:
                        pass
                elif heading and 'working title' in row.text.lower():
                    section = row.find('td')
                    if section:
                        job_title = section.text.replace("\\n",'').replace('\\','')
                        result.append(job_title)
                    else:
                        result.append('Job title missing')
                elif heading and 'additional link' in row.text.lower():
                    section = row.find('td')
                    if section:
                        link = section.find('a')
                        if link:
                            job_url = link['href']
                            result.append(job_url)
                        else:
                            result.append('Job Desc. Unavailable')
                else:
                    pass
            if result:
                all_jobs.append(result)
            else:
                pass
    with open('collected_jobs.txt','w') as outfile:
        for job in all_jobs:
            line = "\t".join(job)
            outfile.write(f"{line}\n")


    



if __name__ == "__main__":
    process_job_posts()
