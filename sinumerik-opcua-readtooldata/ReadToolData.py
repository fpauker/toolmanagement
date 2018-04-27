import argparse
import time
from opcua import Client
from opcua import ua
from opcua import common
import json
import re
import logging
import sys
from sys import stdout
import traceback

# Define logger
logging.basicConfig(stream=stdout,
                    level=logging.ERROR,
                    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s')

logger = logging.getLogger(__name__)

def readalltooldata47(client):
    """
    method for reading the catalogue tooldata for a sinumerk version 4.7
    """
    try:
        paramnumber = (CuttEdgeNum) * numCuttEdgeParams
        logger.info('Parameternumber: {}'.format(paramnumber))
        cuttEdgeParam = client.get_node(ua.NodeId("/Tool/Compensation/cuttEdgeParam[u1,c"+str(toolnumber)+","+str(paramnumber+1)+","+str(paramnumber+34)+"]",2)).get_value()
        data[str(CuttEdgeNum+1)]=[]
        data[str(CuttEdgeNum+1)].append({
            'name': toolname,
            'GWerkzeugtyp:':    cuttEdgeParam[0],
            'GSchneidenlage:':  cuttEdgeParam[1],
            'GLaenge1:':        cuttEdgeParam[2],
            'GLaenge2:':        cuttEdgeParam[3],
            'GLaenge3:':        cuttEdgeParam[4],
            'GRadius:':         cuttEdgeParam[5],
            'GEckenradius:':    cuttEdgeParam[6],
            'GLaenge4:':        cuttEdgeParam[7],
            'GLaenge5:':        cuttEdgeParam[8],
            'GWinkel1:':        cuttEdgeParam[9],
            'GWinkel2:':        cuttEdgeParam[10],
            'VLaenge1:':        cuttEdgeParam[11],
            'VLaenge2:':        cuttEdgeParam[12],
            'VLaenge3:':        cuttEdgeParam[13],
            'VRadius:':         cuttEdgeParam[14],
            'VNutbreite:':      cuttEdgeParam[15],
            'VUeberstand:':     cuttEdgeParam[16],
            'VLaenge5:':        cuttEdgeParam[17],
            'VWinkel1:':        cuttEdgeParam[18],
            'VWinkel2:':        cuttEdgeParam[19],
            'ALaenge1:':        cuttEdgeParam[20],
            'ALaenge2:':        cuttEdgeParam[21],
            'ALaenge3:':        cuttEdgeParam[22],
            'Freischneidwinkel:':                                               cuttEdgeParam[23],
            'Schnittgeschwindigkeit:':                                          cuttEdgeParam[24],
            'HNummer:':                                                         cuttEdgeParam[25],
            'OWerkzeugschneidenorientierung:':                                  cuttEdgeParam[26],
            'OL1KomponenteDerWerkzeugschneidenorientierung:':                   cuttEdgeParam[27],
            'OL2KomponenteDerWerkzeugschneidenorientierung:':                   cuttEdgeParam[28],
            'OL3KomponenteDerWerkzeugschneidenorientierung:':                   cuttEdgeParam[29],
            'OnormierteL1KomponenteDerWerkzeugschneidenorientierung:':          cuttEdgeParam[30],
            'OnormierteL2KomponenteDerWerkzeugschneidenorientierung:':          cuttEdgeParam[31],
            'OnormierteL3KomponenteDerWerkzeugschneidenorientierung:':          cuttEdgeParam[32],
            'AnzahlDerZaehneDerSchneide:':                                      cuttEdgeParam[33]
        })
        logger.info('Successfully collected metadata of tool {}'.format(toolname))
    except Exception as e:
        logger.error('Failed getting metadata of tool {}'.format(toolname))
        logger.debug(traceback.format_exc())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--opcua-connection', type=str, help='Connection string used to connect to the OPC-UA server. e.g. opc.tcp://10.0.22.59:4840/UA/ServerDemo')
    parser.add_argument('--opcua-user', type=str, help='User used for secure connection to OPC-UA server. (optional)', nargs='?')
    parser.add_argument('--opcua-password', type=str, help='Password used to authenticate user on OPC-UA server. (optional)', nargs='?')
    parser.add_argument('--verbose', help='Makes it really chatty.', action="store_true")
    parser.add_argument('--numCuttEdgeParams', type=int, help='Number of cutting edge parameters')
    parser.add_argument('--path', type=str, help='path for storing tool data. Default is in ./tools',default="./tools")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(level=logging.DEBUG)

    try:
        url = re.sub(r"\/\/","//"+args.opcua_user+":"+args.opcua_password+"@",args.opcua_connection)
        opcua_client = Client(url) #connect using a user
        opcua_client.connect()
        logger.info('Successfully connceted to OPC UA server: %s', [args.opcua_connection])
    except Exception as e:
        logger.error('Failed connecting to OPC UA server: %s', [args.opcua_connection])
        logger.debug(traceback.format_exc())
        sys.exit(str(e))

    try:
        #get max number of tools
        TnumWZV = opcua_client.get_node(ua.NodeId("/Tool/Catalogue/TnumWZV",2)).get_value()
        logger.info('Number of available tools: {}'.format(TnumWZV))
        numCuttEdgeParams = args.numCuttEdgeParams

        #get Tooldata for all tools
        for toolnumber in range(1,int(TnumWZV)):
            data = {}
            #get toolnumber for the given TNumber
            try:
                toolname = opcua_client.get_node(ua.NodeId("/Tool/Catalogue/toolIdent["+str(toolnumber)+"]",2)).get_value()
                logger.info('Toolnumber: {}'.format(toolnumber))
            except Exception as e:
                logger.error('Failed getting toolname with number T{}'.format(toolnumber))
                logger.debug(traceback.format_exc())
                continue

            #get number of cutting edges for the given TNumber
            try:
                numCuttEdge = opcua_client.get_node(ua.NodeId("/Tool/Catalogue/numCuttEdges["+str(toolnumber)+"]",2)).get_value()
                logger.info('Number of edges for Tool {}:{}'.format(str(toolname),numCuttEdge))
            except Exception as e:
                logger.error('Failed getting number of edges for tool with number T{}'.format(toolnumber))
                logger.debug(traceback.format_exc())

            for CuttEdgeNum in range(0,int(numCuttEdge)):
                readalltooldata47(opcua_client)
            try:
                re.sub(r"\/","",toolname)
                filepath = args.path +"/"+ toolname + ".json"
                with open(filepath, 'w') as outfile:
                    json.dump(data, outfile, sort_keys=True, indent=2)
                logger.info('Created File: {}'.format(filepath))
            except Exception as e:
                logger.error('Failed writing file {}'.format(filepath))
                logger.debug(traceback.format_exc())
                sys.exit(str(e))
    finally:
        opcua_client.disconnect()
