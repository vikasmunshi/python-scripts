#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    read workshop results from Excel, transform and analyze and dump output to Excel
    requires: numpy pandas neo4j xlrd openpyxl
"""
from os.path import splitext

import pandas as pd
from neo4j import GraphDatabase, basic_auth

default_uri = 'bolt://localhost:7687'
default_user = 'neo4j'
default_pwd = 'YVSJuTtaKlhLZmqT'


def getfilename() -> str:
    import tkinter
    from tkinter import filedialog
    window = tkinter.Tk()
    window.withdraw()
    filename = filedialog.askopenfilename(parent=window, filetypes=[('Excel', '*.xlsx')], title='Choose Excel File')
    window.destroy()
    return filename


def read_transform_dump(filename: str = '', worksheet_name: str = '',
                        label_field: str = '', description_field: str = '', caused_by_field: str = '',
                        uri: str = default_uri, user: str = default_user, password: str = default_pwd,
                        clean_up: bool = False, show: bool = False) -> None:
    # read Excel file and load the contents of the given or last worksheet as data
    with pd.ExcelFile(filename or getfilename()) as workbook:
        data, filename = workbook.parse(worksheet_name or workbook.sheet_names[-1]), workbook.io

    # filter unused columns, simplify names, & transform caused_by column into list
    data = data[[label_field or data.columns[0],
                 description_field or data.columns[1],
                 caused_by_field or data.columns[2]]]
    data.columns = ('label', 'description', 'caused_by')

    # split values in caused_by column on newline and comma
    def splitter(s):
        return [item.strip() for sublist in (line.strip().split(',') for line in s.splitlines()) for item in sublist]

    data.caused_by = data.caused_by.fillna('').apply(splitter)

    # connect to Neo4j instance
    with GraphDatabase.driver(uri, auth=basic_auth(user, password)) as driver:
        # wrapper for executing  parameterized cypher query as a transaction
        def run_graph_trx(cypher_query, **cypher_query_args):
            with driver.session() as session:
                session.write_transaction(lambda tx: tx.run(cypher_query, **cypher_query_args))

        # clear up if asked to
        if clean_up:
            run_graph_trx('MATCH (n:Issues) DETACH DELETE n')

        # add nodes
        add_nodes = 'MERGE (i:%s:Issues {label:$label}) SET i.description = $description'

        def classifier(row):
            return 'Issue' if row.label.endswith('.00') else 'UnderlyingCause' if row.caused_by else 'RootCause'

        data.apply(lambda r: run_graph_trx(add_nodes % classifier(r), label=r.label, description=r.description), axis=1)

        # add relations
        add_relation = 'MATCH (i), (c) WHERE i.label = $label AND c.label = $cause MERGE (i)-[r:CausedBy]->(c)'
        data.apply(lambda r: [run_graph_trx(add_relation, label=r.label, cause=c) for c in r.caused_by], axis=1)

        # calculate rank and add as score
        add_score = 'CALL algo.pageRank("", "", {iterations:25, dampingFactor:0.75, write:true, writeProperty:"score"})'
        run_graph_trx(add_score)

        # query results sorted by score and read as DataFrame
        q = 'MATCH (c)-[:CausedBy]->(i) RETURN i.label AS label, COLLECT(c.label) as leads_to, i.score * 100 as score'
        with driver.session() as query_session:
            results = pd.DataFrame(query_session.run(q).values())

    # join results with data plus list to string conversions and save as Excel
    results.columns = ('label', 'leads_to', 'score')
    results = data.join(results.set_index('label'), on='label').sort_values(by=['score'], ascending=False).fillna('')
    results.caused_by = results.caused_by.apply('\n'.join)
    results.leads_to = results.leads_to.apply('\n'.join)
    results.to_excel('%s_graph_output%s' % (splitext(filename)), index=False)

    # print results if asked for
    if show:
        print(results)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='read, transform, and dump root cause analysis workshop output')
    parser.add_argument('-f', '--filename', default='', help='workshop results file')
    parser.add_argument('--worksheet_name', default='', help='worksheet name, defaults to last worksheet in workbook')
    parser.add_argument('--label_field', default='', help='column to use for label, defaults to first column')
    parser.add_argument('--description_field', default='', help='column for description, defaults to second column')
    parser.add_argument('--caused_by_field', default='', help='column to use for caused_by, defaults to third column')
    parser.add_argument('--uri', default=default_uri, help='neo4j URI, default %s' % default_uri)
    parser.add_argument('-u', '--user', default=default_user, help='neo4j username, default %s' % default_user)
    parser.add_argument('-p', '--password', default=default_pwd, help='password, default %s' % default_pwd)
    parser.add_argument('-c', '--clean_up', action='store_true', help='clean up existing nodes')
    parser.add_argument('-s', '--show', action='store_true', help='print results')

    args = parser.parse_args()

    try:
        read_transform_dump(**vars(args))
    except Exception as e:
        import traceback

        print('Traceback (trace limit 2):')
        traceback.print_tb(e.__traceback__, limit=2)
        print('Exception {} occurred at line {}\n{}'.format(type(e).__name__, e.__traceback__.tb_next.tb_lineno, e))