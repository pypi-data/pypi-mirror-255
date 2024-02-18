from rk.particle_dictionary import particle_dictionary as pdic

#------------------------------
def simple():
    pob  = pdic()
    name = pob.get_particle_name(evtg_name='K_10')
    
    print(name)
#------------------------------
if __name__ == '__main__':
    simple()

