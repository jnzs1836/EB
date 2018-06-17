from pyecharts import Bar, Line, Overlap

attr = [i for i in range(1000)]
v1 = [i for i in range(1000, 2000)]
v2 = [i for i in range(2000, 3000)]
bar = Bar("Line - Bar 示例")
bar.add("bar", attr, v1, is_datazoom_show=True, is_toolbox_show=False)
line = Line()
line.add("line", attr, v2, is_datazoom_show=True, is_toolbox_show=False)


overlap = Overlap()
overlap.add(bar)
overlap.add(line)
overlap.render()