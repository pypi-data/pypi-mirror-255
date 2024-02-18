from rk.br_calculator import br_calculator
import os
import pandas as pnd

#-------------------------------------
def test(mother, dec_file):
    br_cal = br_calculator(mother=mother, dec_file=dec_file)
    br     = br_cal.get_br()

    return br
#-------------------------------------
if __name__ == '__main__':
    br_calculator.output_dir = 'tests/br_calculator/output'
    br_calculator.input_dir  = os.environ['DECDIR']

    bf_bd  = test(     'B0sig', 'bdXcHs.dec')
    bf_abd = test('anti-B0sig', 'bdXcHs.dec')

    bf_bp  = test(     'B+sig', 'bpXcHs.dec')
    bf_bm  = test(     'B-sig', 'bpXcHs.dec')

    df  = pnd.DataFrame({'Sample' : ['B0', 'anti-B0', 'B+', 'B-'], 'Efficiency' : [bf_bd, bf_abd, bf_bp, bf_bm]})
    txt = df.to_latex(index=False)

    ofile=open(f'{br_calculator.output_dir}/summary.tex', 'w')
    ofile.write(txt)
    ofile.close()
#-------------------------------------

