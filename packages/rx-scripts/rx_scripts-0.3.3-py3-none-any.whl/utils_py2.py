import re
import os
import utils_noroot as utnr

log=utnr.getLogger(__name__)
#-------------------------------------------------------
def makeTable(path, l_l_line, caption="", sort = False, form=None, label=None):
    if sort:
        l_l_line.sort()

    ncols=len(l_l_line[0])
    if form is None:
        pass
    elif len(form) != ncols:
        log.error('Formatting string size and ncolumns do not agree: {}/{}'.format(ncols, len(form)))
        raise
    
    l_out=[]
    l_out.append("\\begin{figure}")
    l_out.append("\\centering")
    l_out.append("\\begin{tabular}{ " + "l " * ncols + "}")

    first=True
    for i_row, row in enumerate(l_l_line):
        out=''
        for i_obj, obj in enumerate(row):
            if   form is not None and type(obj) != str:
                formt=form[i_obj]
                obj = formt.format(obj)
            elif form is     None and type(obj) != str:
                obj = '{:.3e}'.format(obj)
                
            try:
                if i_obj == len(row) - 1:
                    out = '{} {} \\\\'.format(out, obj)
                else:
                    out = '{} {} & '.format(out, obj)
            except:
                log.error('Cannot use object {} of type {}'.format(obj, type(obj)))
                raise

        if i_row == len(l_l_line) - 1:
            out=out.replace("\\\\", "")

        l_out.append(out)
        if first:
            l_out.append("\\hline")
            first=False

    l_out.append("\\end{tabular}")
    if caption != "":
        l_out.append("\\caption{%s}" % (caption))
    if label is not None:
        l_out.append("\\label{%s}" % (label))
    l_out.append("\\end{figure}")

    dirname=os.path.dirname(path)
    if not os.path.isdir(dirname)  and dirname != '':
        try:
            os.makedirs(dirname)
        except:
            log.error('Cannot make \'{}\''.format(dirname))
            raise

    ofile=open(path, "w")
    for out in l_out:
        ofile.write(out + "\n")
    ofile.close()
#-------------------------------------------------------

