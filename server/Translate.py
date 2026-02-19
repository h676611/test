#Bruke denne for å oversette requests fra CLI og GUI over til tilsvarende pyvisa requests

def get_dic_for_PSU(psu_name): 
    dic = {# Legger til alle PSU og commandoer inn hær
        "hmp4040": HMP4040_dic,
        "k2400": K2400_dic,
        "k2450": K2450_dic,
        "k6500": K6500_dic
    }
    for psu in dic:
        if psu_name == psu:
            return dic[psu]
    
    raise LookupError(f"can't find dictionary for name {psu_name}")


K6500_dic = {
        #NB: Trailing spaces in these strings are important
        "get_id": "*IDN?",
        "reset": "*RST",
        # "get_error": "SYST:ERR?",
        # "set_source": "SOUR:FUNC ",
        # "get_current": "MEAS:CURR?",
        "get_voltage": "MEAS:VOLT?",
        "set_channel": "route:close",  # NOTE, special set channel treatment below
        "get_channel": "route:multiple:close?",
        "get_channel_voltage": "ROUT:OPEN:ALL;:ROUT:CLOS (@{channel});:READ?"
}

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
            "set_current": "CURR ",
            "set_voltage": "VOLT ",
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