def generate_reply(type, address, response):
    reply = {
        "type": type,
        "address": address,
        "response": response
    }
    if type == "system_reply" or type == "scpi_reply" or type == "error":
        return reply
    else:
        raise TypeError(f"{type} is not a valid reply type")
        

def generate_status_update(state, address):
    reply = {
        "type": "status_update", 
        "status": state, 
        "address": address
        }
    return reply