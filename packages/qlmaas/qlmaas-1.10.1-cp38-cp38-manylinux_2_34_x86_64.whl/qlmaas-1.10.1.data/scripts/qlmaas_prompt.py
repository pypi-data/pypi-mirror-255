#!python
# -*- coding : utf-8 -*-
"""
@authors Simon Martiel <simon.martiel@atos.net>
         Arnaud Gazda <arnaud.gazda@atos.net>
@internal
@copyright 2017-2020  Bull S.A.S.  -  All rights reserved.
           This is not Free or Open Source software.
           Please contact Bull SAS for details about its license.
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois

@file qat-portal/bin/qlmaas_prompt.py
@brief An interactive tool to query QLMaaSConnection
"""

from qat.qlmaas.commands import build_connection


if __name__ == "__main__":
    conn = build_connection("qlmaas_prompt", "Interactive prompt for QLMaaS")
    conn.open_prompt()
