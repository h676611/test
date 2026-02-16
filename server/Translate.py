#Bruke denne for å oversette requests fra CLI og GUI over til tilsvarende pyvisa requests

def get_dic_for_PSU(psu_name): 
    dic = {# Legger til alle PSU og commandoer inn hær
        "HMP4040": HMP4040_dic,
        "K2400": K2400_dic,
        "K2450": K2450_dic,
    }
    for psu in dic:
        if psu_name == psu:
            return dic[psu]

HMP4040_dic = {
    #NB: Trailing spaces in these strings are important
            "get_id": "*IDN?",
            "set_channel": "INST OUT",
            "get_channel": "INST:NSEL?",
            "get_error": "SYST:ERR?",
            "set_output": "OUTP",
            "set_output_all": "OUTP:GEN ",
            "set_source": "SOUR FUNC ",
            #"set_autorange": "SET AUTORANGE CMD",
            "set_current": "CURR",
            "set_voltage": "VOLT",
            "get_current": "MEAS:CURR?",
            "get_voltage": "MEAS:VOLT?",
            "set_current_limit": "VOLT ILIM ",
            "set_voltage_limit": "CURR VLIM ",
            "get_display_current": "CURR?",
            "get_display_voltage": "VOLT?",
            "get_display_output": "OUTP:SEL?",
            "get_current_limit": "VOLT ILIM?",
            "get_voltage_limit": "CURR VLIM?",
            "set_remote": {"mixed": "SYST:MIX", "local": "SYST:LOC",
                           "remote": "SYST:REM"},
            #"get_channel_voltage":         "INST OUT{channel};MEAS:VOLT?",
            #"get_channel_current":         "INST OUT{channel};MEAS:CURR?",
            #"get_channel_set_voltage":     "INST OUT{channel};VOLT?",
            #"get_channel_set_current":     "INST OUT{channel};CURR?",
            #"set_channel_voltage":         "INST OUT{channel};VOLT {voltage}",
            #"set_channel_current":         "INST OUT{channel};CURR {voltage}",
            #"set_channel_current_voltage": "INST OUT{channel};CURR {current};VOLT {voltage}",
            "set_current_voltage": "CURR {current};VOLT {voltage}",

}
K2400_dic = {
    # Note: Some commands may differ on the 2400 vs. 2450.
            # Adjust them if necessary for your particular 2400 SCPI requirements.
            "get_id": "*IDN?",
            "get_error": "SYST:ERR?",
            "set_output": "OUTP ",
            "set_output_all": "OUTP:GEN ",
            "set_source": "SOUR:FUNC ",
            "set_autorange": "SENS:CURR:RANG:AUTO ",
            "set_current_sense_range": "SENS:CURR:RANGE ",
            "set_current": "SOUR:CURR ",
            "set_voltage": "SOUR:VOLT ",
            "set_voltage_range": "SOUR:VOLT:RANG ",
            "get_current": "MEAS:CURR?",
            "get_voltage": "MEAS:VOLT?",
            "set_current_limit": "SOUR:VOLT:ILIMIT ",
            "set_voltage_limit": "SOUR:CURR:VLIMIT ",
            "get_display_current": "SOUR:CURR?",
            "get_display_voltage": "SOUR:VOLT?",
            "get_display_output": "OUTP?",
            "get_current_limit": "SOUR:VOLT:ILIMIT?",
            "get_voltage_limit": "SOUR:CURR:VLIMIT?",
            "set_four_wire_sense": ":SENSe:CURRent:RSENse "
}
K2450_dic = {
      #NB: Trailing spaces in these strings are important
            "get_id": "*IDN?",
            #"set_channel": "SET CHANNEL CMD",
            #"get_channel": "GET CHANNEL CMD",
            "get_error": "SYST:ERR?",
            "set_output": "OUTP ",
            "set_output_all": "OUTP:GEN ",
            "set_source": "SOUR:FUNC ",
            "set_autorange": "SOUR:CURR:RANG:AUTO ",
            "set_current": "SOUR:CURR ",
	        "set_voltage_range": "SOUR:VOLT:RANG ",
            "set_voltage": "SOUR:VOLT ",
            "get_current": "MEAS:CURR?",
            "get_voltage": "MEAS:VOLT?",
            "set_current_limit": "SOUR:VOLT:ILIMIT ",
            "set_voltage_limit": "SOUR:CURR:VLIMIT ",
            "get_display_current": "SOUR:CURR?",
            "get_display_voltage": "SOUR:VOLT?",
            "get_display_output": "OUTP?",
            "get_current_limit": "SOUR:VOLT:ILIMIT?",
            "get_voltage_limit": "SOUR:CURR:VLIMIT?",
            #"set_remote": {"mixed": "SYST:MIX", "local": "SYST:LOC",
            #               "remote": "SYST:REM"}
            "set_four_wire_sense": ":SENSe:CURRent:RSENse "
}