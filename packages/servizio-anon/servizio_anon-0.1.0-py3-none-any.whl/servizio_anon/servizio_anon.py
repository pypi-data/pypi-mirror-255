
def updateAnnotazioni(gatenlpOriginale:dict, risultatoAnalisi:list):
#REQUIRES: Valid GateNLP and a List which contains the results of an analysis run by Presidio
#MODIFIES: input GateNLP
#EFFECTS: Returns a new GateNLP with updated annotations found via Presidio
    annotazioni = gatenlpOriginale['annotation_sets']["entities"]["annotations"]
    nextID = gatenlpOriginale['annotation_sets']["entities"]["next_annid"]

    # Mappiamo le entità per rinominarle
    entity_type_mapping = {
        'PERSON': 'persona',
        'LOCATION': 'indirizzo',
        'IT_FISCAL_CODE':'codice_fiscale',
        'IT_VAT_CODE':'partita_iva'
    }


    for nuovaAnnotazione in risultatoAnalisi:
        mapped_entity_type = entity_type_mapping.get(nuovaAnnotazione.entity_type)

        testoAnnotazione = {    "type": "Word", 
                                "start": nuovaAnnotazione.start, 
                                "end": nuovaAnnotazione.end,
                                "id": nextID,
                                "features": {
                                    "title": gatenlpOriginale["text"][nuovaAnnotazione.start:nuovaAnnotazione.end],
                                    "url": "",
                                    "ner": {
                                        "type": mapped_entity_type,
                                        "normalized_text": gatenlpOriginale["text"][nuovaAnnotazione.start:nuovaAnnotazione.end],
                                    }
                                },
                            }
        nextID += 1
        annotazioni.append(testoAnnotazione)
    
    gatenlpOriginale['annotation_sets']["entities"]["next_annid"] = nextID
    return gatenlpOriginale