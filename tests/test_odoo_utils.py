# tests/test_odoo_client.py
import pytest
import json
from odoo_sales.vault_utils import vault_get_odoo_user, vault_get_odoo_pass
from odoo_sales.odoo_utils import send_notify_email, send_notify_email_failed
from odoo_sales.odoo_utils import get_partner_email, get_or_create_partner 
from odoo_sales.odoo_utils import get_sale_order_lines
from odoo_sales.odoo_utils import create_sale_order

@pytest.mark.skip(reason="temporarily disabled")
def test_get_partner_email():

    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    order_id = 80

    partner_id = get_partner_email(odoo_user, odoo_pass, order_id)
    print("partner_id: ", partner_id)


@pytest.mark.skip(reason="temporarily disabled")
def test_get_sale_order_lines():

    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    order_id = 80

    order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
    print("order_lines: ", order_lines)



@pytest.mark.skip(reason="temporarily disabled")
def test_send_notify_email():
    
    staff_email = "cshwk2020@gmail.com"
    order_id = 78
    email_data_json = [
        {
            "id": "19e38d9b29c16735",
            "threadId": "19e38d9b29c16735",
            "labelIds": [
            "UNREAD",
            "Label_6658174428264408620",
            "IMPORTANT",
            "CATEGORY_PERSONAL",
            "INBOX"
            ],
            "sizeEstimate": 8706,
            "headers": {
            "delivered-to": "Delivered-To: cshwk2020@gmail.com",
            "received": "Received: from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41])\r\n        by mx.google.com with SMTPS id 98e67ed59e1d1-369b500c525sor416524a91.10.2026.05.17.19.10.51\r\n        for <cshwk2020@gmail.com>\r\n        (Google Transport Security);\r\n        Sun, 17 May 2026 19:10:51 -0700 (PDT)",
            "x-received": "X-Received: by 2002:a17:90a:c42:b0:369:7421:6d2b with SMTP id\r\n 98e67ed59e1d1-3697421b9e8mr4210768a91.19.1779070251052; Sun, 17 May 2026\r\n 19:10:51 -0700 (PDT)",
            "arc-seal": "ARC-Seal: i=1; a=rsa-sha256; t=1779070251; cv=none;\r\n        d=google.com; s=arc-20240605;\r\n        b=lPqpmneyq3nVUIYSjFWJ4JRJZH0dlVayhXJ8qmj2zzJxYIcZv/o/o1UkgkjbeCzk3z\r\n         a0klvK2hC9q5fLAqWC0qaX9OBXMFWgFBrfI67FuTfx8Gd0jG655O2lknyjCWXMMv3rWr\r\n         6HzMjSQtyuDRp60WofNRzkGQxs10RdqDkis9JxQgPTv3zzRbkGcEQqCpkvrxuH/Lqpxu\r\n         1x07eXreXhQqmdO6ufDXGCgJlPDRuxCQA/qm9rEv/6w7kpSNtx4OVF+MdStohhcycc3n\r\n         ly5o7/BLdcp77t5mjWXQnULgTNfNUByanCfvZbjpQPoIgbvHXrBWCLlWBa4kMfnWE7/5\r\n         CPNQ==",
            "arc-message-signature": "ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20240605;\r\n        h=to:subject:message-id:date:from:mime-version:dkim-signature;\r\n        bh=PukBnJtF9K4iD48SrVz0DQRYsht/Cr2EYwrP8XqjT7Y=;\r\n        fh=hyD13cRnBqlXoivBIuubKqg6DOz+JJE/rhoafzGUWSY=;\r\n        b=YlxfgOYlw1Jni/C8SUTdVogMr5bAqjpW4QRydM9QVUgT57QMbwcHsIg83hpTsEhazg\r\n         XU7VVwEfGx3Z0UZdmnxvyuCobLHxDLgb95qprh2JV/+fje5kdVgElu7XYP77ZtBYsYBZ\r\n         4rFbr45Q3+z7UZrRcjCj/DPOdvkgow1uVWQJrpXspvEH9nImdsV/nrrFak9pZWJ2SY/m\r\n         oe4ITXP+UYj1yfy0Nfl86Bxg2npFiTlsHM2w7MAwq2Uz7K55p6vLW0RXaIqH5LyFKzH9\r\n         /wAIisPL9DkusC27hgr6tkLGjh3Vav0nMgwxuw6hIQ2+ow30bWQ2hgZrbmPRMzFUodk5\r\n         Nr5A==;\r\n        dara=google.com",
            "arc-authentication-results": "ARC-Authentication-Results: i=1; mx.google.com; arc=none",
            "return-path": "Return-Path: <cshwk2021@gmail.com>",
            "received-spf": "Received-SPF: pass (google.com: domain of cshwk2021@gmail.com designates 209.85.220.41 as permitted sender) client-ip=209.85.220.41;",
            "authentication-results": "Authentication-Results: mx.google.com;\r\n       dkim=pass header.i=@gmail.com header.s=20251104 header.b=rbNlrRXa;\r\n       arc=pass (i=1);\r\n       spf=pass (google.com: domain of cshwk2021@gmail.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=cshwk2021@gmail.com;\r\n       dmarc=pass (p=NONE sp=QUARANTINE dis=NONE) header.from=gmail.com;\r\n       dara=pass header.i=@gmail.com",
            "dkim-signature": "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=gmail.com; s=20251104; t=1779070251; x=1779675051; dara=google.com;\r\n        h=to:subject:message-id:date:from:mime-version:from:to:cc:subject\r\n         :date:message-id:reply-to;\r\n        bh=PukBnJtF9K4iD48SrVz0DQRYsht/Cr2EYwrP8XqjT7Y=;\r\n        b=rbNlrRXa+QFjpi4Y34XeQUrwC26ULfsmJOSmKVlIuumj0TDa1YW6gT/FFgwkstRFMW\r\n         ZhGGWdnaTwHCALCLChGrh+B8QOSXjl3hCQ+hWx1UWR0JGqndEDKPscLM0Mjq013B9JbK\r\n         23Q8DnupZBz1NfPplaETvwdv41+9H4Bk0RLQhJDPwpIercgEnmENooWwefCTF1pfufIN\r\n         vyBW3/7fNcxSINZRobA+eQDdVi8Glx8c2iX03iB4KmEkPfcFkdyUlS23Hc1PeldwHCQu\r\n         nsT8fEFK8UBQOG3eyZpRYgj7LA8g2lm5UeFKtgVxPH45NjhnLZt/4nOzCXWUKOxRQZCG\r\n         /qBA==",
            "x-google-dkim-signature": "X-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=1e100.net; s=20251104; t=1779070251; x=1779675051;\r\n        h=to:subject:message-id:date:from:mime-version:x-gm-gg\r\n         :x-gm-message-state:from:to:cc:subject:date:message-id:reply-to;\r\n        bh=PukBnJtF9K4iD48SrVz0DQRYsht/Cr2EYwrP8XqjT7Y=;\r\n        b=TCI0Nlbz5DXFe7wV1EFLDAuM4PWev9eH0vbZryIWeqQpuQuDW0HWonIqPXw4XBWB6n\r\n         pIansK6re/pkvaK5QSsjj3NeumTwvUy12/L/qEDGxMSP4rj+2IHD6AHISh1e8st5pjTF\r\n         6Le0gkUUe45+uFifCKDUumaUnQiiNDEoeUGxKiJUcenRun0F7OszvA72tTwyxfxVqWLi\r\n         jAI1ocw/gktZ9kVPX7lEU3ogcuFq+397r3s5niEFDRHIim95l9deowSufZ+kiwOdx5/H\r\n         WUgozB5sb9kc5iR0q6MVer8NJR7YB7xMc5XoMFF9BBAa90MDod87UqqEBB+kH26vchtK\r\n         dAeQ==",
            "x-gm-message-state": "X-Gm-Message-State: AOJu0YxkyhQdPvA6uwqZZ22TxRrxAuObwdd0mCeCfiRsDatUHORuzhxM\r\n\tT8+cAGpiFwTEleXfISHt/Xg2kXl0mhyN5tykwpYZT44KJRGm09ugbJA43ALCBWmOdN/q4ztlz+R\r\n\t58AQa2+L/cnBADvk3eQP9ABUEMPkTwaeAPsebXdQ=",
            "x-gm-gg": "X-Gm-Gg: Acq92OFDjPnrU8VK1DhAydI37iyVYvPz4APfQ7UQRtsqb+bYEbi1vLfg0EkrTHTV+Z/\r\n\tZOdZ4y0xjNFOcEKCJ+n4z8P/ptxF/JwkXVVrXc1693TmiazPjzPuB0bviDxguX3pAcCE67yG6K0\r\n\tzm3/n/lHj0tKb+kjwugBPW1w2f3oGLDJ/oGQKsg4e5UHE2LC1wbGEQqtyNRglgB+0hKYknC/zFj\r\n\tOuLaKfdyCPJslER3Vq2gfy7YhJNTyLLEBcl3KRb8HDMiNFmlwkSMAxpq742IcE8rbJrnDERgsOP\r\n\t0qCzP6ZvlRb1YwaCxOlooQ/1a5RxvMFBzoUryw==",
            "mime-version": "MIME-Version: 1.0",
            "from": "From: hung wai kay <cshwk2021@gmail.com>",
            "date": "Date: Mon, 18 May 2026 10:11:15 +0800",
            "x-gm-features": "X-Gm-Features: AVHnY4JaAUZK_84OvQo8FJ5gtlCcd0qrSDQy8E2jBNtyqGRVvMmhkhZNhISv1tg",
            "message-id": "Message-ID: <CAHuSHOhxkKQ16QSGVtYSHDBfGgSwQKB2fgQnpVyP4bfsYXSgrQ@mail.gmail.com>",
            "subject": "Subject: request order QuoTATion [ uc: ALL VALID ]",
            "to": "To: \"cshwk2020@gmail.com\" <cshwk2020@gmail.com>",
            "content-type": "Content-Type: multipart/alternative; boundary=\"0000000000005834d106520e1200\""
            },
            "html": "<div dir=\"ltr\"><div class=\"gmail-gE gmail-iv gmail-gt\" style=\"font-size:0.875rem;padding:20px 0px 0px;font-family:&quot;Google Sans&quot;,Roboto,RobotoDraft,Helvetica,Arial,sans-serif\"><span style=\"background-color:rgb(245,245,245);color:rgb(68,140,39);font-family:Menlo,Monaco,&quot;Courier New&quot;,monospace;font-size:12px;white-space:pre-wrap\">Dear customer service manager, </span><table cellpadding=\"0\" class=\"gmail-cf gmail-gJ\" style=\"border-collapse:collapse;margin-top:0px;width:auto;font-size:0.875rem;display:block\"></table></div><div class=\"gmail-\" style=\"font-family:&quot;Google Sans&quot;,Roboto,RobotoDraft,Helvetica,Arial,sans-serif;font-size:medium\"><div class=\"gmail-ii gmail-gt\" id=\"gmail-:qg\" style=\"direction:ltr;margin:8px 0px 0px;padding:0px;font-size:0.875rem;overflow-x:hidden\"><div class=\"gmail-a3s gmail-aiL\" id=\"gmail-:qf\" style=\"direction:ltr;font-style:normal;font-variant:normal;font-size-adjust:none;font-kerning:auto;font-feature-settings:normal;font-stretch:normal;font-size:small;line-height:1.5;font-family:Arial,Helvetica,sans-serif;overflow:auto hidden\"><div id=\"gmail-avWBGd-80\"><div dir=\"ltr\"><div style=\"color:rgb(51,51,51);background-color:rgb(245,245,245);font-family:Menlo,Monaco,&quot;Courier New&quot;,monospace;font-size:12px;line-height:18px;white-space:pre-wrap\"><div><span style=\"color:rgb(68,140,39)\">        need a StainlessKettle, a great coffee machine, a new microwave oven </span></div><div><span style=\"color:rgb(68,140,39)\">        thx, kk</span></div></div></div></div></div></div></div></div>\n",
            "text": "Dear customer service manager,\nneed a StainlessKettle, a great coffee machine, a new microwave oven\nthx, kk\n",
            "textAsHtml": "<p>Dear customer service manager,<br/>need a StainlessKettle, a great coffee machine, a new microwave oven<br/>thx, kk</p>",
            "subject": "request order QuoTATion [ uc: ALL VALID ]",
            "date": "2026-05-18T02:11:15.000Z",
            "to": {
            "value": [
                {
                "address": "cshwk2020@gmail.com",
                "name": ""
                }
            ],
            "html": "<span class=\"mp_address_group\"><a href=\"mailto:cshwk2020@gmail.com\" class=\"mp_address_email\">cshwk2020@gmail.com</a></span>",
            "text": "cshwk2020@gmail.com"
            },
            "from": {
            "value": [
                {
                "address": "cshwk2021@gmail.com",
                "name": "hung wai kay"
                }
            ],
            "html": "<span class=\"mp_address_group\"><span class=\"mp_address_name\">hung wai kay</span> &lt;<a href=\"mailto:cshwk2021@gmail.com\" class=\"mp_address_email\">cshwk2021@gmail.com</a>&gt;</span>",
            "text": "\"hung wai kay\" <cshwk2021@gmail.com>"
            },
            "messageId": "<CAHuSHOhxkKQ16QSGVtYSHDBfGgSwQKB2fgQnpVyP4bfsYXSgrQ@mail.gmail.com>"
        }
    ]

    send_notify_email(staff_email, order_id, email_data_json)



@pytest.mark.skip(reason="temporarily disabled")
def test_send_notify_email_failed():

    staff_email = "cshwk2020@gmail.com"

    email_data_json = {
        "id": "19e24bfcfdff4583",
        "threadId": "19e24bfcfdff4583",
        "labelIds": [
        "UNREAD",
        "Label_6658174428264408620",
        "CATEGORY_PERSONAL",
        "INBOX"
        ],
        "sizeEstimate": 7141,
        "headers": {
        "delivered-to": "Delivered-To: cshwk2020@gmail.com",
        "received": "Received: from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41])\r\n        by mx.google.com with SMTPS id a640c23a62f3a-bd4fd1671ecsor9804566b.9.2026.05.13.21.30.10\r\n        for <cshwk2020@gmail.com>\r\n        (Google Transport Security);\r\n        Wed, 13 May 2026 21:30:10 -0700 (PDT)",
        "x-received": "X-Received: by 2002:a17:907:d02:b0:bc4:b981:d6eb with SMTP id\r\n a640c23a62f3a-bd4f35039e9mr128310766b.29.1778733009515; Wed, 13 May 2026\r\n 21:30:09 -0700 (PDT)",
        "arc-seal": "ARC-Seal: i=1; a=rsa-sha256; t=1778733010; cv=none;\r\n        d=google.com; s=arc-20240605;\r\n        b=Rz0mmW0wvOi41Ur9qPwOJNArwrbOcJLDHg1BMch9w+YI00l//nXZPlCcixNkggsKwB\r\n         mp+v2bCs+LkY5eTYf359uI5aP2LqwRrAPbGDPvo4AW9pzkc427X/d0dMYxkP90LsHaiJ\r\n         BZXPYmKdu/G7JwJ0yt/tvUbEHiesOogUEzUch9vbiW9YLKja+yACa3GHOFmYizxjPkKZ\r\n         eo7jnKb0YK9OtOB1TUayBW0ayMWoLKycEKmrl+1+0792YaTCcwlrfByHuWTHwmVuRPzN\r\n         I+2vWYCRSmY6xgt+OpOd8sbq+/uzFrhOgmJPKSxmvzQMuarp0isHzZvETtHSsKXZpiZd\r\n         j/yw==",
        "arc-message-signature": "ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20240605;\r\n        h=to:subject:message-id:date:from:mime-version:dkim-signature;\r\n        bh=Ncg2ukjY0PAKnOQisyaqSy6uQOOAR7nSFYC2wpubZs0=;\r\n        fh=hyD13cRnBqlXoivBIuubKqg6DOz+JJE/rhoafzGUWSY=;\r\n        b=kIhmm9GvDxkxZojfJTiEmbuHxmj2DktPzhyrbVsZnIkdbaVnDbTGNPbg4iNxm80nlX\r\n         dMT6pE4h+RRk6gURkXDsQfoamtXYkF1KYWxJZnV7ugFgfDSr77T4o8t3ViCZCsWM5WHb\r\n         rEKTQ0sh3kNvZy8SUGekGtmY+/6gaRTRZJRHhcPpn3T0tju2ftBwSNsAChZx1jsJVbAl\r\n         z+0SPB7EQ+hfbrwOqCC+Wb0Bs+HoE2O6gf7KRipO8hNyNy42WyPhvKY2vIbyNwpgL4KD\r\n         lZy7C1Njh2KpY1JMye2Pg5JV5QHrohx9aOxLiRAwJZKAGGtsmuZ3jjaEBlLeWYBgapgr\r\n         2G6Q==;\r\n        dara=google.com",
        "arc-authentication-results": "ARC-Authentication-Results: i=1; mx.google.com; arc=none",
        "return-path": "Return-Path: <cshwk2021@gmail.com>",
        "received-spf": "Received-SPF: pass (google.com: domain of cshwk2021@gmail.com designates 209.85.220.41 as permitted sender) client-ip=209.85.220.41;",
        "authentication-results": "Authentication-Results: mx.google.com;\r\n       dkim=pass header.i=@gmail.com header.s=20251104 header.b=R4pgks3u;\r\n       arc=pass (i=1);\r\n       spf=pass (google.com: domain of cshwk2021@gmail.com designates 209.85.220.41 as permitted sender) smtp.mailfrom=cshwk2021@gmail.com;\r\n       dmarc=pass (p=NONE sp=QUARANTINE dis=NONE) header.from=gmail.com;\r\n       dara=pass header.i=@gmail.com",
        "dkim-signature": "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=gmail.com; s=20251104; t=1778733010; x=1779337810; dara=google.com;\r\n        h=to:subject:message-id:date:from:mime-version:from:to:cc:subject\r\n         :date:message-id:reply-to;\r\n        bh=Ncg2ukjY0PAKnOQisyaqSy6uQOOAR7nSFYC2wpubZs0=;\r\n        b=R4pgks3uQcvrMPLMnkzHQRQtNS8uu7ntP4RZGT0RgT8M5o8oOw5Vn64sf2zQIcSIzu\r\n         BpHIOYHEbbMqeGo2eglHTXiakZjjfvu9MVSBg6BawKDo0LOlgWl9ly3kqjn/N9CR9P1n\r\n         mBa3LQ5mLTQ/M2jC+0cExG5ejytmDF0ONlaoeb3xZAcOTisUawuJbt/PEsof2iYrrAtt\r\n         M65DuT3Pd/2FrCGKHgHPHsY5/JDwSg+S0xI4iYhLbnHV7mmnENk1dGtDxM1L3gjGKKbb\r\n         NVe9f5kBrrplgkI3oDEaVB9q0MSNc63xbHcYZrziAjr5diFs/d6JaA0DmyDRfZLDxXa4\r\n         XADg==",
        "x-google-dkim-signature": "X-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=1e100.net; s=20251104; t=1778733010; x=1779337810;\r\n        h=to:subject:message-id:date:from:mime-version:x-gm-gg\r\n         :x-gm-message-state:from:to:cc:subject:date:message-id:reply-to;\r\n        bh=Ncg2ukjY0PAKnOQisyaqSy6uQOOAR7nSFYC2wpubZs0=;\r\n        b=H/cqQup2SZN/dgJDQRmyjY2genm9BrwPO3GqCQmlAR/lUneAsUvy+YAQM1CrArhNvQ\r\n         n35ItvWHz2r3wG3nRfBEC44RxAaCAhGplHSiYLHXa8N3fmf7lAwNmSuUqODn43holUmI\r\n         m/uY2Jt1BaiN0I+kFjSm7KQfRCLdKjwY9qVHWrcdb2yB8fsp8wldfZYvWc3AtyjwsfG2\r\n         XIceNt+F3nfQOWNHLU2LsUUYwcz7h3jpASMV5lNZrCm2CnhiLrDMKmHh7WaZWuaddX7y\r\n         vyiIlk/X3rdNo0j8NujVi6u1jAP9qJvjLf5xfwoHD5IuvOeU6fUB0nkvUSnvBK3dv3z7\r\n         8yqA==",
        "x-gm-message-state": "X-Gm-Message-State: AOJu0YzuR5oA0yItv5lhEHvnBXU7tm+vQtm3Gg3+n0CegpRZE4HI7716\r\n\tx6H2HAp133jBHVAXlI16LqxoY979jskBRpKKqL6RjwbKea5nA8Wr3jmU2EYQ4cu9WK4m+Iv2VKq\r\n\tHmriRe4CClLtzZzqeBi0m4B4msgxSoJ4g7YGqGtE=",
        "x-gm-gg": "X-Gm-Gg: Acq92OGtfeUvzlAS/cpOmG9uLobWNaAmBjnoIX5QBWckEsmWIwS6QqVN3rgIqtAz9WX\r\n\trLg2Tr+NwSLd4t1iwivjlvZscE2MQoXg4BvCML6nLi35jrD0IYsCQ4p8ienw/s6WrAFr9TCBckj\r\n\tfXMBrm6Epdre871v6dnjZzAZwh4HCoWKqEfKQd+M1BUT9aHxyUJ7xAhYTGUBJviACpcsbg9a6L6\r\n\tH6eBJYVL5HQyPmH6YDx3z6N+ybxD7M6YT+jNxQgKgYIXSZyDcpoAs3+E6CFkANXBy7j3Q1nn3lT\r\n\tPvlxaTx+iqc1TYh9gN9RBcGGWVhQP4QmXXQJQkLcOEQPJUM=",
        "mime-version": "MIME-Version: 1.0",
        "from": "From: hung wai kay <cshwk2021@gmail.com>",
        "date": "Date: Thu, 14 May 2026 12:31:25 +0800",
        "x-gm-features": "X-Gm-Features: AVHnY4I1Tbmf1_nS3ZS3eg5I0pjZgK4WqW2Cr9IuYS-TQfzEsOv9QN8Eh9e1w40",
        "message-id": "Message-ID: <CAHuSHOihCaJw8w6wRXrmW7AqfD1MGOMTmXD0gjXHKr9ydRZ25w@mail.gmail.com>",
        "subject": "Subject: request order QuoTATion",
        "to": "To: \"cshwk2020@gmail.com\" <cshwk2020@gmail.com>",
        "content-type": "Content-Type: multipart/alternative; boundary=\"0000000000002eb6d10651bf8d8f\""
        },
        "html": "<div dir=\"ltr\">Dear customer service manager,<br><br>need a StainlessKettle, a great coffee machine, a new microwave oven<br><br>thx,<br>kk</div>\n",
        "text": "Dear customer service manager,\n\nneed a StainlessKettle, a great coffee machine, a new microwave oven\n\nthx,\nkk\n",
        "textAsHtml": "<p>Dear customer service manager,</p><p>need a StainlessKettle, a great coffee machine, a new microwave oven</p><p>thx,<br/>kk</p>",
        "subject": "request order QuoTATion",
        "date": "2026-05-14T04:31:25.000Z",
        "to": {
        "value": [
            {
            "address": "cshwk2020@gmail.com",
            "name": ""
            }
        ],
        "html": "<span class=\"mp_address_group\"><a href=\"mailto:cshwk2020@gmail.com\" class=\"mp_address_email\">cshwk2020@gmail.com</a></span>",
        "text": "cshwk2020@gmail.com"
        },
        "from": {
        "value": [
            {
            "address": "cshwk2021@gmail.com",
            "name": "hung wai kay"
            }
        ],
        "html": "<span class=\"mp_address_group\"><span class=\"mp_address_name\">hung wai kay</span> &lt;<a href=\"mailto:cshwk2021@gmail.com\" class=\"mp_address_email\">cshwk2021@gmail.com</a>&gt;</span>",
        "text": "\"hung wai kay\" <cshwk2021@gmail.com>"
        },
        "messageId": "<CAHuSHOihCaJw8w6wRXrmW7AqfD1MGOMTmXD0gjXHKr9ydRZ25w@mail.gmail.com>"
    }


    send_notify_email_failed(staff_email, order_id, email_data_json)



@pytest.mark.skip(reason="temporarily disabled")
def test_create_sale_order_uc_all_incomplete():

    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    order_id = 80
 
    partner_email = get_partner_email(odoo_user, odoo_pass, order_id) 
    partner_id = get_or_create_partner(odoo_user, odoo_pass, partner_email)

    email_data_json = {
        "id": "19e3428760cd3ad1", 
        "threadId": "19e3428760cd3ad1",
        "snippet": "need a ABCX and HEJKX thx, kk",
        
        "payload": {
            "mimeType": "multipart/alternative"
        },

        "sizeEstimate": 12983,
        "historyId": "969584",
        "internalDate": "1778991551000",
        
        "labels": [
            {
            "id": "INBOX",
            "name": "INBOX"
            },
            {
            "id": "IMPORTANT",
            "name": "IMPORTANT"
            },
            {
            "id": "CATEGORY_PERSONAL",
            "name": "CATEGORY_PERSONAL"
            },
            {
            "id": "UNREAD",
            "name": "UNREAD"
            },
            {
            "id": "Label_6658174428264408620",
            "name": "SaleOrder" 
            }
        ],
        
        "From": "hung wai kay <cshwk2021@gmail.com>",
        "Subject": "request order QuoTATion",
        "To": "\"cshwk2020@gmail.com\" <cshwk2020@gmail.com>"
    }

    parsed_items = [
        {'input': 'ABCX', 'candidates': [], 'qty': 1, 'status': 'not_found'}, 
        {'input': 'HEJKX', 'candidates': [], 'qty': 1, 'status': 'not_found'}
    ]

    sale_items = [
        {'name': None, 'qty': 1, 'confidence': 0.0, 'remark': 'no candidates found', 'status': 'error', 'input': 'ABCX'}, 
        {'name': None, 'qty': 1, 'confidence': 0.0, 'remark': 'no candidates found', 'status': 'error', 'input': 'HEJKX'}
    ]

    odoo_result = create_sale_order(odoo_user, odoo_pass, partner_id, email_data_json, parsed_items, sale_items)
    #
    staff_email = email_data_json.get("To")
    original_email_body = email_data_json["snippet"]
    order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)

    send_notify_email_failed(staff_email, order_id, original_email_body)
    print("result: ", json.dumps(odoo_result))



@pytest.mark.skip(reason="temporarily disabled")
def test_create_sale_order_uc_all_complete():

    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    order_id = 80
 
    partner_email = get_partner_email(odoo_user, odoo_pass, order_id) 
    partner_id = get_or_create_partner(odoo_user, odoo_pass, partner_email)
    email_data_json = {
        "id": "19e3428760cd3ad1", 
        "threadId": "19e3428760cd3ad1",
        "snippet": """
            Dear customer service manager, 
            need a StainlessKettle, a great coffee machine, a new microwave oven 
            thx, kk
        """,
        
        "payload": {
            "mimeType": "multipart/alternative"
        },

        "sizeEstimate": 12983,
        "historyId": "969584",
        "internalDate": "1778991551000",
        
        "labels": [
            {
            "id": "INBOX",
            "name": "INBOX"
            },
            {
            "id": "IMPORTANT",
            "name": "IMPORTANT"
            },
            {
            "id": "CATEGORY_PERSONAL",
            "name": "CATEGORY_PERSONAL"
            },
            {
            "id": "UNREAD",
            "name": "UNREAD"
            },
            {
            "id": "Label_6658174428264408620",
            "name": "SaleOrder" 
            }
        ],
        
        "From": "hung wai kay <cshwk2021@gmail.com>",
        "Subject": "request order QuoTATion",
        "To": "\"cshwk2020@gmail.com\" <cshwk2020@gmail.com>"
    }
    
  
    parsed_items = [
        {'input': 'StainlessKettle', 'candidates': ['stainless steel kettle', 'stainless kettle'], 'qty': 1, 'status': 'ambiguous'}, 
        {'input': 'great coffee machine', 'candidates': ['coffee machine'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'new microwave oven', 'candidates': ['microwave oven'], 'qty': 1, 'status': 'exact'}
    ]
 
    sale_items = [
        {'name': 'Electric Kettle Stainless Steel', 'qty': 1, 'confidence': 0.95, 'remark': 'clear winner', 'status': 'complete'}, 
        {'name': 'Coffee Maker Capsule', 'qty': 1, 'confidence': 0.95, 'remark': 'clear winner', 'status': 'complete'}, 
        {'name': 'Microwave Oven Compact', 'qty': 1, 'confidence': 0.95, 'remark': 'clear winner', 'status': 'complete'}
    ]
 
    odoo_result = create_sale_order(odoo_user, odoo_pass, partner_id, email_data_json, parsed_items, sale_items)
    
    #
    staff_email = email_data_json.get("To")
    order_id = odoo_result['order_id']
    original_email_body = email_data_json["snippet"]
    order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
    send_notify_email(staff_email, order_id, original_email_body, order_lines)
    
    print("odoo_result: ", odoo_result)



@pytest.mark.skip(reason="temporarily disabled")
def test_create_sale_order_uc_partial_complete():

    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    order_id = 80

    partner_id = get_partner_email(odoo_user, odoo_pass, order_id) 
    email_data_json = {
        "id": "19e3428760cd3ad1", 
        "threadId": "19e3428760cd3ad1",
        "snippet": """
            Dear customer service manager, 
            need a StainlessKettle, a ABCX, a new microwave oven 
            thx, kk
        """,
        
        "payload": {
            "mimeType": "multipart/alternative"
        },

        "sizeEstimate": 12983,
        "historyId": "969584",
        "internalDate": "1778991551000",
        
        "labels": [
            {
            "id": "INBOX",
            "name": "INBOX"
            },
            {
            "id": "IMPORTANT",
            "name": "IMPORTANT"
            },
            {
            "id": "CATEGORY_PERSONAL",
            "name": "CATEGORY_PERSONAL"
            },
            {
            "id": "UNREAD",
            "name": "UNREAD"
            },
            {
            "id": "Label_6658174428264408620",
            "name": "SaleOrder" 
            }
        ],
        
        "From": "hung wai kay <cshwk2021@gmail.com>",
        "Subject": "request order QuoTATion",
        "To": "\"cshwk2020@gmail.com\" <cshwk2020@gmail.com>"
    }

    parsed_items = [
        {'input': 'StainlessKettle', 'candidates': ['stainless steel kettle', 'StainlessKettle'], 'qty': 1, 'status': 'ambiguous'}, 
        {'input': 'ABCX', 'candidates': [], 'qty': 1, 'status': 'not_found'}, 
        {'input': 'microwave oven', 'candidates': ['microwave oven'], 'qty': 1, 'status': 'exact'}
    ]

    sale_items = [
        {'name': 'Electric Kettle Stainless Steel', 'qty': 1, 'confidence': 0.95, 'remark': 'clear winner', 'status': 'complete'}, 
        {'name': 'Unisex Hoodie Graphic', 'qty': 1, 'confidence': 0.3, 'remark': 'gap is tight, not safe', 'status': 'incomplete'}, 
        {'name': 'Coffee Maker Capsule', 'qty': 1, 'confidence': 0.9, 'remark': 'clear winner', 'status': 'complete'}
    ]

    odoo_result = create_sale_order(odoo_user, odoo_pass, partner_id, email_data_json, parsed_items, sale_items)
    
    #
    staff_email = email_data_json.get("To")
    order_id = odoo_result.get('order_id')
    original_email_body = email_data_json["snippet"]
    order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
    send_notify_email(staff_email, order_id, original_email_body, order_lines)
    
    print("odoo_result: ", odoo_result)
