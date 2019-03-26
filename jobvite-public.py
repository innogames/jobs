#!/usr/bin/env python3

import requests
import xmltodict
import html2markdown
import re

COMPANY_ID = 'qyy9VfwU'
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


def get_listings():
    r = requests.get(JOBVITE_XML)
    jobs = xmltodict.parse(r.text)

    return(dict(jobs))


def get_job_details(job_id):
    r = requests.get(JOBVITE_XML + '&j=' + job_id)
    job_details = xmltodict.parse(r.text)

    return(dict(job_details['result']))


def sanitize_url(input_str, dedup_char, offset=0, out=''):
    for i in [' ', '[', ']', '(', ')', '/', '\\', '?', '*']:
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


def render_job_markdown(job):
    markdown = '# {}\n\n'.format(job['title'])
    markdown += html2markdown.convert(job['description'])
    markdown += '\n\n## [Apply Now]({}&__jvst={}&i__jvsd={})'.format(
            job['apply-url'], JOBVITE_SOURCE_TYPE, JOBVITE_SOURCE_DETAIL)
    markdown += ' directly or get more [Information]'
    markdown += '({}?s={}) about InnoGames'.format(
            get_homepage_url(job), JOBVITE_SOURCE_DETAIL)

    # manually clean some wierdness
    r = re.compile(r"^__ \s+", re.MULTILINE)
    markdown = r.sub('__', markdown.replace('____', ''))
    r = re.compile(r"\s+\n\s*__\n", re.MULTILINE)
    markdown = r.sub('__\n', markdown.replace('&nbsp;__','__'))


    return(markdown)


def render_readme(jobs):
    markdown = '# Open Positions @ [InnoGames]({}?s={})\n\n'.format(
            HOMEPAGE_BASE, JOBVITE_SOURCE_DETAIL)
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
            f.write(render_job_markdown(job_details))
            f.close()

    f = open('README.md', 'w')
    f.write(render_readme(jobs))
    f.close()


if __name__ == '__main__':
    main()
