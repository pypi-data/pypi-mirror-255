from rk.pulls import plot_pulls as pltp

#-------------------------------
def test():
    pull_dir = 'tests/pulls/0p010_000'

    po = pltp(dir_name = pull_dir)
    po.plot_dir = 'tests/plot_pulls'
    po.save_plots(d_name = {'mu' : '$\mu$', 'sg' : '$\sigma$', 'nev' : '$N_{signal}$'})
#-------------------------------
if __name__ == '__main__':
    test()

