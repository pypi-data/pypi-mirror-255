from rk.sample_tools import get_decay_from_evt

#--------------------------------
def get_evt():
    l_evt=[]
    l_evt.append('12155110')
    l_evt.append('12103025')
    l_evt.append('12153012')
    l_evt.append('15454101')
    l_evt.append('12143001')
    l_evt.append('12425000')
    l_evt.append('12153001')
    l_evt.append('12143020')
    l_evt.append('13454001')
    l_evt.append('12425011')
    l_evt.append('12123445')
    l_evt.append('12153020')
    l_evt.append('12952000')
    l_evt.append('11453001')
    l_evt.append('12143010')
    l_evt.append('11154001')
    l_evt.append('12155100')
    l_evt.append('11154011')
    l_evt.append('12183004')
    l_evt.append('12583013')
    l_evt.append('12113002')
    l_evt.append('12583021')
    l_evt.append('11124002')
    l_evt.append('12123003')
    l_evt.append('12123445')
    l_evt.append('12103025')
    l_evt.append('12155110')
    l_evt.append('12123444')
    l_evt.append('12123005')
    l_evt.append('12123002')
    l_evt.append('12113001')
    l_evt.append('11124001')

    return l_evt
#--------------------------------
class data:
    l_evt = get_evt()
#------------------------------------
def test_evt_dec():
    for evt in data.l_evt:
        dec = get_decay_from_evt(evt)
        print(dec)
#------------------------------------
if __name__ == '__main__':
    test_evt_dec()

