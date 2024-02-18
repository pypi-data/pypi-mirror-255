#! /usr/bin/python 
# -*- coding: utf-8 -*-

import logging
    
def tratado_log(origen,destino):
    
    file = open(origen, 'r')
    
    logging.basicConfig(filename=destino, encoding='utf-8' , level=logging.DEBUG)
    
    lines = file.read().splitlines()
    file.close()
    
    for item in lines:
        if "[root]" in item:
            logging.debug(item)
        
if __name__=='__main__':
    
    origen="/home/agv/catkin_ws/src/API_AGV_NODO_24-5-2023_15-46-30.log"
    
    destino='/home/agv/catkin_ws/src/API_AGV_CLIENT.log'
    
    tratado_log(origen,destino)
