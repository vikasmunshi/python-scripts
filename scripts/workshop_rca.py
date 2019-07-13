#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    read workshop results from Excel, transform and analyze and dump output to Excel
    requires: numpy pandas neo4j xlrd openpyxl
"""
from os.path import splitext

import pandas as pd
from neo4j import GraphDatabase

default_uri = 'bolt://localhost:7687'
default_user = 'neo4j'
default_pwd = 'YVSJuTtaKlhLZmqT'


def getfilename():
    import tkinter as tk
    from tkinter import filedialog as fd
    window = tk.Tk()
    window.withdraw()
    fn = fd.askopenfilename(parent=window, filetypes=[('Excel', '*.xlsx')], title='Choose Graph Data File')
    window.destroy()
    return fn


def read_transform_dump(filename: str = '', worksheet_name: str = '',
                        id_field: str = '', description_field: str = '', causes_field: str = '',
                        uri: str = default_uri, user: str = default_user, password: str = default_pwd,
                        clean_up: bool = False, show: bool = False) -> None:
    # read Excel file and load the contents of the given or last worksheet as data
    with pd.ExcelFile(filename or getfilename()) as workbook:
        data = workbook.parse(worksheet_name or workbook.sheet_names[-1])
        filename = workbook.io if not filename else filename

    # filter unused columns, simplify names, drop rows with no value in the causes column, transform causes into list
    data = data[[id_field or data.columns[0], description_field or data.columns[1], causes_field or data.columns[2]]]
    data.columns = ('id', 'description', 'causes')
    data = data.dropna(axis=0, subset=['causes'])
    # split causes on newline and comma, remove RC
    data['causes'] = data.causes.apply(lambda x: tuple(c for c in (
        i.strip() for s in (r.strip().split(',') for r in x.splitlines()) for i in s) if c != 'RC'))

    # connect to Neo4j instance
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        # wrapper for executing  parameterized cypher query as a transaction
        def run_graph_transaction(cypher_query, **cypher_query_args):
            with driver.session() as session:
                session.write_transaction(lambda tx: tx.run(cypher_query, **cypher_query_args))

        # clear up if asked to
        if clean_up:
            run_graph_transaction('MATCH (n:Issue) DETACH DELETE n')

        # add nodes
        add_nodes = 'MERGE (i:%s:Issue {label:$label}) SET i.description = $description'
        data.apply(lambda r: run_graph_transaction(add_nodes % (
            'Result' if r.id.endswith('.00') else 'RootCause' if not r.causes else 'UnderlyingCause'),
                                                   label=r.id, description=r.description), axis=1)
        # add relations
        add_relation = 'MATCH (i), (c) WHERE i.label = $label AND c.label = $cause MERGE (i)-[r:CausedBy]->(c)'
        data.apply(lambda r: tuple(run_graph_transaction(add_relation, label=r.id, cause=c) for c in r.causes),
                   axis=1)
        # calculate rank and add as score
        add_score = 'CALL algo.pageRank("", "", {iterations:25, dampingFactor:0.75, write:true, writeProperty:"score"})'
        run_graph_transaction(add_score)

        # query results sorted by score and read as DataFrame
        query = """MATCH (c)-[:CausedBy]->(i) 
                        RETURN i.label AS ID, i.description as Description, COLLECT(c.label) as Causes, i.score as Score 
                        ORDER BY i.score DESC"""
        with driver.session() as query_session:
            results = pd.DataFrame(query_session.run(query).values())

        # rename column names, change score to int, and save as Excel
        results.columns = ('ID', 'Description', 'Leads To', 'Score')
        results['Score'] = results.Score.apply(lambda s: int(100 * s))
        results.to_excel('%s_graph_output%s' % (splitext(filename)), index=False)

        # print results if asked for
        if show:
            print(results)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='read, transform, and dump root cause analysis workshop output')
    parser.add_argument('-f', '--filename', default='', help='workshop results file')
    parser.add_argument('--worksheet_name', default='', help='worksheet name, defaults to last worksheet in workbook')
    parser.add_argument('--id_field', default='', help='column to use for id, defaults to first column')
    parser.add_argument('--description_field', default='', help='column for description, defaults to second column')
    parser.add_argument('--causes_field', default='', help='column to use for causes, defaults to third column')
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
