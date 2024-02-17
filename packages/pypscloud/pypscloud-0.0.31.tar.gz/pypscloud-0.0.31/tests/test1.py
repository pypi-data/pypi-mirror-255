import sys
import os
sys.path.append(os.path.abspath("/Users/lmarchand.PS/PycharmProjects/pypscloud/pypscloud"))

from pypscloud import *


def test_site(ps):
    mps = ps.get_all_mp_from_account(6)
    for mp in mps:
        accountId = mp['accountId']
        siteId = mp['locationId']
        site = ps.get_site(mp['locationId'])
        if site['locationName'] == 'PQube3 e Test wall':
            print(mp)
            print(site)
            new_site = site
            del new_site['locationId']
            del new_site['measurementPoints']
            new_site['locationName'] = 'PQube3 e Test wall 09'

            ps.set_site(accountId, siteId, new_site)


def test_all_mps_accounts(ps):
    df = ps.get_all_mps_from_all_accounts_as_df()
    print(df)


def test_tz():
    s, e = ps_build_start_end_date_from_midnight(7, 'America/Los_Angeles')
    print(s)
    print(e)

    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/Los_Angeles')
    print(d)
    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/New_York')
    print(d)
    ss = ps_time_with_tz(s, 'America/Los_Angeles')
    print(ss)
    ee = ps_time_with_tz(e, 'America/Los_Angeles')
    print(ee)


def main():
    ps = PSCommon('prod')
    s3 = PSS3
    
    ps.login()
    #ps_post_cmd(13817,7)

    #ps.device_file_request_by_mp(16667, ["channels-P3020805.json"])

    #test_site(ps)
    #test_all_mps_accounts(ps)
    #cd = ps.get_mp_channel_def(15206)
    #hb = ps.get_mp_heartbeat(20247, 2)
    #print(hb)
    #test_tz()
    p = ps.get_mp_parameters(15206)
    print(p)

main()