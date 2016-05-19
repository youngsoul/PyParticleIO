from pyparticleio import ParticleCloud

c = ParticleCloud.ParticleCloud(username_or_access_token='7daf320fc0e2860b8134ed6f353c4107129dee51')
#print(c.devices)

for i in range(0,8):
    print("Analog Offset {0} = {1}".format(i, c.internet_button2.getAnalogOff("{0}".format(i))))

for i in range(0,8):
    offset = i*100
    result = c.internet_button2.setAnalogOff("{0},{1}".format(i,offset))
    print("Set Analog Offset 100*{0}, result: {1}".format(i, result))

for i in range(0,8):
    print("Analog Offset {0} = {1}".format(i, c.internet_button2.getAnalogOff("{0}".format(i))))

for i in range(0,8):
    offset = 0
    result = c.internet_button2.setAnalogOff("{0},{1}".format(i,offset))
    print("Set Analog Offset to 0, result: {1}".format(i, result))

for i in range(0,8):
    print("Previous Analog Value {0} = {1}".format(i, c.internet_button2.getPrevAna("{0}".format(i))))
