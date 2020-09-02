# Version 0.25 of bibtex graph visualizer

# Contact: jdmorise a t yahoo.com

# Copyright (c) 2015-2019
# 

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------------------------------------------------------
# Changelog: 
# v0.25: 
#        Bug Fix of graph generation
#        
# 
# ------------------------------------------------------------------------------------------------------------------------------
# v0.24: 
#        Added level and years (before and after) for reduction of the graph. 
#        Fixed Bug for Calculation of number o publications with timed filters
# 

import argparse
import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from authors import Authors, AuthorsGraph
from semantics import Semantic, SemanticGraph


def BuildAuthorGraph(args):
    G = AuthorsGraph()

    print("""A Graph Display Software for bibtex databases
    Copyright (C) 2015 JD Morise, jdmorise a t yahoo.com
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. 
    
    """)

    # thresholds
    G.edge_rel_thr = args.edge_relation_thres
    G.aut_rel_thr = args.author_relation_thres
    G.aut_pub_thr = args.author_publication_thres
    G.level = args.level

    MyParser = BibTexParser()
    MyParser.customization = convert_to_unicode

    print('Inputfile: ' + args.input_filename)

    with open(args.input_filename) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=MyParser)

    # construct array of authors
    #

    main_author_name = args.main_author_name.split(' ')

    MyAuthors = Authors(main_author_name[0], main_author_name[-1])

    MyAuthors.after = args.after
    MyAuthors.before = args.before

    MyAuthors.create_author_list(bib_database)

    # construct array of relationsships
    MyAuthors.create_relations(bib_database)

    # Add Nodes to Graph
    G.add_author_nodes(MyAuthors)

    # Add Edges to Graph
    G.add_author_edges(MyAuthors)

    # remove nodes with no connection
    G.remove_author_nodes()

    print('Render Graph')
    G.write('debug.dot')

    G.layout(prog=args.graph_programm)
    G.draw(args.graph_filename)
    print('Graph file written to: ' + args.graph_filename)
    return 0


def BuildSemanticGraph(args):
    MyParser = BibTexParser()
    MyParser.customization = convert_to_unicode

    print('Inputfile: ' + args.input_filename)

    with open(args.input_filename) as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=MyParser)
    S = Semantic(bib_database, args.topics)
    G = SemanticGraph()
    G.add_tags_nodes(S)
    G.add_paper_nodes(S)
    G.add_paper_edges(S)

    print('Render Graph')
    G.write('debug.dot')

    G.layout(prog=args.graph_programm)
    G.draw(args.graph_filename)
    print('Graph file written to: ' + args.graph_filename)
    return 0


if __name__ == "__main__":
    usage = """"Examples: """
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-if', '--input_filename', help='Filename of publication database in bibtex format')
    parser.add_argument('-gf', '--graph_filename', default='graph.png', help='Filename of graph output stored as png')
    parser.add_argument('-ma', '--main_author_name', default='Max Mustermann')
    parser.add_argument('-ert', '--edge_relation_thres', type=int, default=1, help='Only add edges with ERT or more number of relations')
    parser.add_argument('-art', '--author_relation_thres', type=int, default=1, help='Only add authors with ART or more number of relations')
    parser.add_argument('-apt', '--author_publication_thres', type=int, default=1, help='Only add authors with APT number of publications')
    parser.add_argument('-lvl', '--level', type=int, default=256)
    parser.add_argument('-b', '--before', type=int, default=2050, help='Only use Publications before YEAR for the graph')
    parser.add_argument('-a', '--after', type=int, default=1900, help='Only use Publications after YEAR for the graph')
    parser.add_argument('-t', '--type', default='author', help='Build either semantic or author relation graph')
    parser.add_argument('-o', '--topics', default=None, nargs='+', help='Select the semantic topics to use (case insensitive)')

    parser.add_argument('-gp', '--graph_programm', default='fdp', help="""Graph Programm for rendering the graph. one of the following: fdp,dot,sfdp,circo,twopi.""")

    args = parser.parse_args()

    if args.type.lower() == 'author':
        sys.exit(BuildAuthorGraph(args=args))
    elif args.type.lower() == 'semantic':
        sys.exit(BuildSemanticGraph(args=args))
