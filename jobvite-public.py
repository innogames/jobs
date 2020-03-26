#!/usr/bin/env python3

import requests
import xmltodict

COMPANY_ID = 'qyy9VfwU'
COMPANY_NAME = 'InnoGames'
JOBVITE_XML = 'https://app.jobvite.com/CompanyJobs/Xml.aspx?c={}&cf=e'.format(
        COMPANY_ID)
CATEGORIES = ['Development',
              'Quality Assurance',
              'System Administration',
              'Office IT']
CUSTOM_SUB_CATEGORIES_ALL = ['Development & IT']
CUSTOM_SUB_CATEGORIES_CAT_ONLY = ['Career Starters']
JOBVITE_SOURCE_TYPE = 'Job+Board'
JOBVITE_SOURCE_DETAIL = 'github_jobs_repo'
HOMEPAGE_BASE = 'https://www.innogames.com/career/detail/job'
JOBVITE_DIRECT = 'https://jobs.jobvite.com/careers/innogames/job/'
TEASER_TEXT='# Open Positions @ [InnoGames]({}?s={})\n\n'.format(
            HOMEPAGE_BASE, JOBVITE_SOURCE_DETAIL)

def get_listings():
    r = requests.get(JOBVITE_XML)
    jobs = xmltodict.parse(r.text)

    return(dict(jobs))


def get_job_details(job_id):
    r = requests.get(JOBVITE_XML + '&j=' + job_id)
    job_details = xmltodict.parse(r.text)

    return(dict(job_details['result']))


def sanitize_url(input_str, dedup_char, offset=0, out=''):
    for i in [' ', '[', ']', '(', ')', '/', '\\', '?', '*', ':']:
        input_str = input_str.replace(i, '-')

    for c in input_str:
        if offset > 0 and c == dedup_char and out[offset - 1] == dedup_char:
            continue
        else:
            out += c
        offset += 1

    return out


def get_homepage_url(job):
    url = HOMEPAGE_BASE
    sanitized = sanitize_url(job['title'], '-').lower()
    url = HOMEPAGE_BASE + '/' + sanitized + '/'

    return(url)


def render_job(job):
    rendered = '<h1>{}</h1>\n'.format(job['title'])
    rendered += job['description']
    rendered += '\n\n<h2><a href="{}/{}/apply?__jvst={}&__jvsd={}">Apply Now</a> ' \
        'directly or get more <a href="{}?s={}">Information</a> about {}</h2>'.format(
                    JOBVITE_DIRECT,
                    job['id'],
                    JOBVITE_SOURCE_TYPE,
                    JOBVITE_SOURCE_DETAIL,
                    get_homepage_url(job),
                    JOBVITE_SOURCE_DETAIL,
                    COMPANY_NAME)
    return(rendered)


def render_readme(jobs):
    markdown = TEASER_TEXT
    for job in jobs['result']['job']:
        if job['subcategory'] in CUSTOM_SUB_CATEGORIES_ALL or (
                job['subcategory'] in CUSTOM_SUB_CATEGORIES_CAT_ONLY and
                job['category'] in CATEGORIES):
            filename = sanitize_url(
                    job['title'], '-').strip('-').lower() + '.md'
            markdown += '### [{}]({})\n'.format(
                    job['title'].replace('(', '\(').replace(')', '\)'),
                    filename)

    return(markdown)


def main():
    jobs = get_listings()

    for job in jobs['result']['job']:
        if job['subcategory'] in CUSTOM_SUB_CATEGORIES_ALL or (
                job['subcategory'] in CUSTOM_SUB_CATEGORIES_CAT_ONLY and
                job['category'] in CATEGORIES):
            job_details = get_job_details(job['id'])

            filename = sanitize_url(
                    job['title'], '-').strip('-').lower() + '.md'
            f = open(filename, 'w')
            f.write(render_job(job_details))
            f.close()

    f = open('README.md', 'w')
    f.write(render_readme(jobs))
    f.close()


if __name__ == '__main__':
    main()
