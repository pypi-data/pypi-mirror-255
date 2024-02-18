from rk.decay_finder import event_dictionary as evt_dic

#--------------------------
def test():
    obj  =evt_dic()
    d_evt=obj.get()
#--------------------------
if __name__ == '__main__':
    test()

