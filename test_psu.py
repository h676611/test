import pyvisa
rm = pyvisa.ResourceManager('dummy_psu.yaml@sim')
inst = rm.open_resource('ASRL1::INSTR')
print(inst.query("PING"))