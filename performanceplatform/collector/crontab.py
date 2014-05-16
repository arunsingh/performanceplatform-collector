import argparse
import re
import sys


ignore_line_re = re.compile("^#.*|\s*$")


class ParseError(StandardError):
    pass


def crontab_begin_comment(unique_id):
    return '# Begin performanceplatform.collector jobs for %s' % unique_id


def crontab_end_comment(unique_id):
    return '# End performanceplatform.collector jobs for %s' % unique_id


def remove_existing_crontab_for_app(crontab, unique_id):
    new_crontab = []
    should_append = True
    for line in crontab:
        if line == crontab_begin_comment(unique_id):
            should_append = False
        if should_append:
            new_crontab.append(line)
        if line == crontab_end_comment(unique_id):
            should_append = True
    return new_crontab


def parse_job_line(line):
    """
    >>> parse_job_line( \
            "* * * *,myquery,mycredentials,mytoken,performanceplatform\\n")
    ('* * * *', 'myquery', 'mycredentials', 'mytoken', 'performanceplatform')
    >>> parse_job_line("            ") is None
    True
    >>> parse_job_line("# comment") is None
    True
    """
    parsed = None

    if not ignore_line_re.match(line):
        parsed = tuple(line.strip().split(','))

    return parsed


def generate_crontab(current_crontab, path_to_jobs, path_to_app, unique_id):
    """Returns a crontab with jobs from job path

    It replaces jobs previously generated by this function
    It preserves jobs not generated by this function
    """
    job_template = '{schedule} {python} {app_path}/main.py ' \
                   '-q {app_path}/config/{query} ' \
                   '-c {app_path}/config/{credentials} ' \
                   '-t {app_path}/config/{token} ' \
                   '-b {app_path}/config/{performanceplatform} ' \
                   '>> {app_path}/log/out.log 2>> {app_path}/log/error.log'

    crontab = [line.strip() for line in current_crontab]
    crontab = remove_existing_crontab_for_app(crontab, unique_id)
    additional_crontab = []
    with open(path_to_jobs) as jobs:
        try:
            for job in jobs:
                parsed = parse_job_line(job)

                if parsed is not None:
                    schedule, query, credentials, \
                        token, performanceplatform = parsed

                    cronjob = job_template.format(
                        schedule=schedule,
                        python=sys.executable,
                        app_path=path_to_app,
                        query=query,
                        credentials=credentials,
                        token=token,
                        performanceplatform=performanceplatform
                    )

                    additional_crontab.append(cronjob)

        except ValueError as e:
            raise ParseError(str(e))

    if additional_crontab:
        crontab.append(crontab_begin_comment(unique_id))
        crontab.extend(additional_crontab)
        crontab.append(crontab_end_comment(unique_id))

    return crontab


if __name__ == '__main__':
    current_crontab = sys.stdin.readlines()
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('path_to_app',
                            help='Path to where the application')
        parser.add_argument('path_to_jobs',
                            help='Path to the file where job templates are')
        parser.add_argument('app_unique_id',
                            help='Unique id of the application '
                                 'used to update crontab')

        args = parser.parse_args()

        crontab = generate_crontab(current_crontab,
                                   args.path_to_jobs,
                                   args.path_to_app,
                                   args.app_unique_id)
        sys.stdout.write("\n".join(crontab) + "\n")
        sys.exit(0)
    except StandardError as e:
        sys.stderr.write(str(e))
        sys.stdout.write("\n".join(current_crontab))
        sys.exit(1)