#!/usr/bin/env python3

import requests
import json

COMPANY_ID = 'innogames'
COMPANY_NAME = 'InnoGames'
LEVER_JSON = 'https://api.eu.lever.co/v0/postings/{}?mode=json'.format(
        COMPANY_ID)
TEAMS = [
    'Analytics',
    'Art', 
    'Community Management',
    'CRM',
    'Finance',
    'Game Design',
    'Human Resources',
    'Legal',
    'Management',
    'Marketing',
    'Office IT',
    'Office Management',
    'Product Management',
    'Public Relations',
    'Quality Assurance',
    'Software Development',
    'System Administration',
    'Career Starters",
]

LEVER_SOURCE_TYPE = 'Job+Board'
LEVER_SOURCE_DETAIL = 'github_jobs_repo'
HOMEPAGE_BASE = 'https://www.innogames.com/career'
TEASER_TEXT='# Open Positions @ [InnoGames]({}?s={})\n\n'.format(
            HOMEPAGE_BASE, LEVER_SOURCE_DETAIL)

def get_listings():
    r = requests.get(LEVER_JSON, stream=True)
    jobs = json.loads(r.text)
    return(jobs)


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
    sanitized = sanitize_url(job['text'], '-').lower()
    url = HOMEPAGE_BASE + '/' + sanitized + '/'

    return(url)


def render_job(job):
    rendered = '<h1>{}</h1>\n'.format(job['text'])
    rendered += job['descriptionPlain']
    rendered += '\n\n<h2><a href="{}">Apply Now</a> ' \
        'directly or get more <a href="{}">Information</a> about {}</h2>'.format(
                    job['applyUrl'],
                    job['hostedUrl'],
                    COMPANY_NAME)
    return(rendered)


def render_readme(jobs):
    markdown = TEASER_TEXT
    for job in jobs:
        if 'team' in job['categories'] and job['categories']['team'] in TEAMS:
            filename = sanitize_url(
                    job['text'], '-').strip('-').lower() + '.md'
            markdown += '### [{}]({})\n'.format(
                    job['text'].replace('(', '\(').replace(')', '\)'),
                    filename)

    return(markdown)


def main():
    jobs = get_listings()

    for job in jobs:
        if 'team' in job['categories'] and job['categories']['team'] in TEAMS:
            filename = sanitize_url(
                    job['text'], '-').strip('-').lower() + '.md'
            f = open(filename, 'w')
            f.write(render_job(job))
            f.close()

    f = open('README.md', 'w')
    f.write(render_readme(jobs))
    f.close()


if __name__ == '__main__':
    main()
