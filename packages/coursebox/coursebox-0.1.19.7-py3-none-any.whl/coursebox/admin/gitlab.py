import datetime

import gitlab
import gitlab.const
from urllib.parse import urlparse

domain = urlparse('http://www.example.test/foo/bar').netloc
print(domain) # --> www.example.test

def sync_tas_with_git():
    from coursebox import class_information # Put this here so information is synced.
    info = class_information()
    url = info['project_correction_url']
    domain = urlparse(url).netloc

    # curl --header "PRIVATE-TOKEN: glpat--NYfBQfTS9JW2G7uPmM2" "https://gitlab.example.com/api/v4/projects/cp%2F02002instructors/members/all"
    gl = gitlab.Gitlab(url="https://"+domain, private_token=info['instructor_gitlab_token'].strip())
    a = 234
    prs = []
    name = url.split(domain)[-1][1:]
    p = gl.projects.get(name)

    users = p.users.list()

    all_tas = [u.name for u in users]
    for i in info['instructors']:
        if i['name'] not in all_tas:
            print(i)
    for i in p.invitations.list():
        print("Invited", i.invite_email.split("@"))

    if True:
        for i in info['instructors']:
            # i = info['instructors'][2]
            if i['email'].split("@")[0].strip() in all_tas:
                print("TA found already", i['name'], i['email'])
            else:
                import datetime
                expires = datetime.datetime.now() + datetime.timedelta(days=30*5+14)
                expires_str =expires.strftime('%A %b %d, %Y at %H:%M GMT')

                inv = p.invitations.create({
                    "email": i['email'], # '"fmry@dtu.dk",
                    "access_level": gitlab.const.AccessLevel.MAINTAINER,
                    "expires_at": expires_str,
                })
                inv.save()
                print("Inviting...", i['email'], i['name'])

    # for p in gl.projects.list(iterator=True):
    #     prs.append(p)
    # for p in prs:
    #     # print(p.name)
    #     if "02002" in p.name:
    #         print(p.name, p.id)
    #
    # p = gl.projects.get(1644)
    # users = p.users.list(get_all=True)
    # for u in users:
    #     print(u)


    # p.invitations.get("tuh@dtu.dk")

    # gl.users.list()[1].username
