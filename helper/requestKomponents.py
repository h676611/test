def generateRequest(type, address, id, payload=[]):
    reply = {
        "type": type,
        "address": address,
        "id": id,
        "payload": payload
    }
    if type == "system_request" or type ==  "scpi_request":
        return reply
    return "Error: Type not system_request or scpi_request"
        