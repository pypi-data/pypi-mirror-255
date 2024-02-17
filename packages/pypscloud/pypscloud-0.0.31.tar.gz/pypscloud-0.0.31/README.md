# pypscloud
Common wrappers and tools in Python for the Powerside Cloud API

Environments and credentials can be configure using this json file format
[
    {
        "env": "production",
        "user": "your account@company.com",
        "pw": "GreatNews123!",
        "base_url": "https://www.admin.cloud.powerside.com/v1/",
        "data_bucket_upload":"bucked-name",
        "aws_key":"if_you_have_one",
        "aws_secret":"dont_share_it"
    },
    {
        "env": "staging",
        "user": "your_account_in_staging@company.com",
        "pw": "thepassword33456!",
        "base_url": "https://staging.admin.cloud.powerside.com/v1/",
        "data_bucket_upload":"bucked-name",
        "aws_key":"if_you_have_one",
        "aws_secret":"dont_share_it"
    }
]