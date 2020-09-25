import pygraphviz as pgv


class Semantic(object):

    def __init__(self, bibsource, tags=None):
        # TODO: Support grouping tags
        # The list of tags
        self.bibsource = bibsource
        self.list_of_tags = tags
        if self.list_of_tags is None:
            self.list_of_tags = []
            for bibentry in self.bibsource.entries:
                try:
                    for tag in bibentry['mendeley-tags'].split(','):
                        if tag not in self.list_of_tags:
                            self.list_of_tags.append(tag)
                except KeyError:
                    # bibentry doesn't have mendeley-tags
                    pass
        self.list_of_tags = [x.lower() for x in self.list_of_tags]


class SemanticGraph(pgv.AGraph):
    def __init__(self):
        # colors
        self.my_colorscheme = 'X11'
        self.paper_fill_color = 'deepskyblue2'
        self.tag_fill_color = '#ebe134'
        self.node_outline_color = 'navy'
        self.edge_color = 'black'
        self.node_font_color = 'navy'
        self.aut_pub_thr = 1
        self.aut_edge_thr = 1
        self.edge_rel_thr = 1
        self.level = 1
        self.before = 0
        self.after = 0
        super(SemanticGraph, self).__init__(strict=False, directed=False, splines=True, style='filled', colorscheme=self.my_colorscheme)

        self.tag_ids = {}

    def add_tags_nodes(self, semantics):
        import random
        random.seed(1234)
        r = lambda: random.randint(100, 255)

        for idx, tag in enumerate(semantics.list_of_tags):
            graph_label = '{tag}&#92;n'.format(tag=tag)
            self.tag_ids[tag] = idx
            self.add_node(idx, label=graph_label, style='filled', color=self.node_outline_color, penwidth=3, fillcolor='#%02X%02X%02X' % (r(), r(), r()), fontcolor=self.node_font_color)
            #self.node_attr.update(style='filled', color=self.node_outline_color, penwidth=3, fillcolor=self.tag_fill_color, fontcolor=self.node_font_color)

    def add_paper_nodes(self, semantics):
        for idx, paper in enumerate(semantics.bibsource.entries, start=len(semantics.list_of_tags)):
            graph_label = '{author}, {year}&#92;n'.format(author=paper['author'].split(',')[0], year=paper['year'])

            self.add_node(idx, label=graph_label, style='filled', color=self.node_outline_color, penwidth=3, fillcolor=self.paper_fill_color, fontcolor=self.node_font_color)
            #self.node_attr.update(style='filled', color=self.node_outline_color, penwidth=3, fillcolor=self.paper_fill_color, fontcolor=self.node_font_color)

    def add_paper_edges(self, semantics):
        for paper_id, paper in enumerate(semantics.bibsource.entries, start=len(semantics.list_of_tags)):
            try:
                has_tag = False
                for paper_tag in paper['mendeley-tags'].split(','):
                    if paper_tag.lower() in semantics.list_of_tags:
                        self.add_edge(paper_id, self.tag_ids[paper_tag.lower()], label='', weigth=2, dir='none', penwidth=1, color=self.edge_color)
                        has_tag = True
                if not has_tag:
                    print('\033[93mWarning:\033[0m Removing node from graph --> no tags-connection: \033[94m{}\033[0m'.format(paper['title']))
                    self.remove_node(self.get_node(paper_id))

            except KeyError:
                # paper doesn't have mendeley-tags, so flag remove color to indicate it will not have any connections
                print('\033[93mWarning:\033[0m Removing node from graph --> no mendeley-tags: \033[94m{}\033[0m'.format(paper['title']))
                self.remove_node(self.get_node(paper_id))

                #n.attr['fillcolor'] = 'white'
