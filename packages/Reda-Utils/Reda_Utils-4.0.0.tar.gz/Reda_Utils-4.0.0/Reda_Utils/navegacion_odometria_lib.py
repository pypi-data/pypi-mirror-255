#!/usr/bin/python
# -*- coding: UTF-8 -*-

import rospy,sys,traceback

from copy import deepcopy 
from geometry_msgs.msg import *
from std_msgs.msg import *
from sensor_msgs.msg import *
from nav_msgs.msg import * 
from math import *

""" 
    Navegación de un robot diferencial mediante su odometría.
    
    Recibe como objetivo pose ( respecto al robot ). Necesita también recibir la odometría a través de _recibir_odom().
    
    Velocidad lineal a 0.35 m/s y a 0.1 m/s cuando distancia es menor que 0.25 m.
    
    Velocidad angular (R) a 350 grados/min (~0.1 rad/s) y a 0.04 rad/s cuando el giro es menor de 20 grados.
    
    { Depende de Reda_Utils } 
    
"""

try: 
    
    import Reda_Utils.Utils as utils
    nav_utils=utils.Nav_utils()
    
except Exception:
    
    raise Exception(traceback.format_exc())


home='/home/agv'
#with open(home+"/catkin_python3/src/cart_detection/cfg/GLVARS.yaml") as f:
#    config_=yaml.load(f, Loader=yaml.FullLoader)

velocidad_pub = rospy.Publisher('MAQUINA/cmd_vel',Twist, queue_size=1)

#### variables

class Variables_nav_odom():

    vel= 0.35 #config_['vel']['value']*60  # m/min
    velgiro= 350 #config_['velgiro']['value']*pi/180.0 #grados/min a rad/min
    velang_min=350 #config_['velang_min']['value']*pi/180.0
    
    Posicion_Alcanzada=False
    odom_diferencial=Pose2D()
    odom_referencia=Pose2D()
    odom_recibida=Pose2D()
    
    pto_objetivo=Pose2D()
    margen_objetivo_x=0.02
    margen_objetivo_y=0.02
    margen_objetivo_th=radians(2)
    
    delta=Pose2D()
    
    odom_disponible=False
    
    pto_objetivo_disponible=False
    
variables=Variables_nav_odom()

def _salir():
    sys.exit()

##### funcion giro

def _giro(objetivo_giro=float):
    
    print('\nGIRANDO : '+str(round(degrees(objetivo_giro),2))+' GRADOS\n')
    
    wd,wi=nav_utils.giro(objetivo_giro,vel_giro=variables.velgiro,vel_angular_min=variables.velang_min)
    vel_msg_Twist=nav_utils.w_wheels_Twist_diferencial(wd,wi,vel_lineal_max=variables.vel,vel_lineal_min=variables.vel,vel_angular_max=variables.velgiro,vel_angular_min=variables.velang_min) 
    
    #wd,wi=nav_utils.mixto_diferencial_sin()
    
    return vel_msg_Twist

##### funcion avanzar

def _avanzar(dist):
    
    print('\nAVANZANDO')
    
    wd,wi=nav_utils.recto_diferencial(dir=1,vel_lineal=variables.vel)
    vel_msg_Twist=nav_utils.w_wheels_Twist_diferencial(wd,wi,vel_lineal_max=variables.vel,vel_lineal_min=variables.vel,vel_angular_max=variables.velgiro,vel_angular_min=variables.velang_min)
    
    return vel_msg_Twist

##### funcion marcha atras

def _marcha_atras(dist):
    
    print('\nMARCHA ATRAS')
    
    wd,wi=nav_utils.recto_diferencial(dir=-1,vel_lineal=variables.vel)
    vel_msg_Twist=nav_utils.w_wheels_Twist_diferencial(wd,wi,vel_lineal_max=variables.vel,vel_lineal_min=variables.vel,vel_angular_max=variables.velgiro,vel_angular_min=variables.velang_min)
    
    return vel_msg_Twist

##### funcion recibir_odom

def _recibir_odom(odom_recibida=Pose2D):
    """
    + Cada vez que recibe la odometria actualiza la posicion odometrica diferencial y con esta actualiza tambien la posicion actual
    """    
    variables.odom_recibida.x=odom_recibida.x
    variables.odom_recibida.y=odom_recibida.y
    variables.odom_recibida.theta=odom_recibida.theta
    
    #### posicion odometrica diferencial
    variables.odom_diferencial.x=variables.odom_recibida.x-variables.odom_referencia.x
    variables.odom_diferencial.y=variables.odom_recibida.y-variables.odom_referencia.y
    variables.odom_diferencial.theta=variables.odom_recibida.theta-variables.odom_referencia.theta   
    
    #variables.odom_diferencial.theta=variables.odom_diferencial.theta%(2*pi)
    
    ## navegacion.poseactual=variables.odom_diferencial
    
    variables.delta.x=variables.pto_objetivo.x-variables.odom_referencia.x-variables.odom_diferencial.x
    variables.delta.y=variables.pto_objetivo.y-variables.odom_referencia.y-variables.odom_diferencial.y
    variables.delta.theta=variables.pto_objetivo.theta-variables.odom_referencia.theta-variables.odom_diferencial.theta
    
    if variables.delta.x==-0.0:             ## para evitar el fallo de atan2(-0,0)=180
        variables.delta.x=abs(variables.delta.x)
    if variables.delta.y==-0.0:
        variables.delta.y=abs(variables.delta.y)
            
    variables.odom_disponible=True
        
    return

##### funcion reiniciar odom

def _reiniciar_odom():
    
    variables.odom_referencia.x=deepcopy(variables.odom_recibida.x)
    variables.odom_referencia.y=deepcopy(variables.odom_recibida.y)
    variables.odom_referencia.theta=deepcopy(variables.odom_recibida.theta)
    
    return

def comprobar_objetivo_llegada():
            
    ### Creo limites para comprobar si el punto actual (diferencial odom), con los margenes, coincide con el punto objetivo
    
    lim_x_inf=(-variables.margen_objetivo_x)
    lim_x_sup=variables.margen_objetivo_x
    
    lim_y_inf=(-variables.margen_objetivo_y)
    lim_y_sup=variables.margen_objetivo_y
    
    lim_th_inf=(-variables.margen_objetivo_th)
    lim_th_sup=variables.margen_objetivo_th
               
    
    if (lim_x_inf <=  variables.delta.x <= lim_x_sup) and (lim_y_inf <=  variables.delta.y <= lim_y_sup) and (lim_th_inf <=  variables.delta.theta <= lim_th_sup):
            
        Posicion_Alcanzada=True
                
    else:
            
        Posicion_Alcanzada=False
    
    variables.Posicion_Alcanzada=Posicion_Alcanzada
    
    print('\n')
    rospy.loginfo ('VELS:  LINEAL= %.2f , GIRO= %.2f, GIRO_MIN= %.2f',round(variables.vel,2),round(degrees(variables.velgiro),2),round(degrees(variables.velang_min),2))
    rospy.loginfo ('Pose_objetivo:  X= %.2f , Y= %.2f, Theta= %.2f',round(variables.pto_objetivo.x,2),round(variables.pto_objetivo.y,2),round(degrees(variables.pto_objetivo.theta),2))
    rospy.loginfo ('Pose_odom:      X= %.2f , Y= %.2f, Theta= %.2f',round(variables.odom_recibida.x,2),round(variables.odom_recibida.y,2),round(degrees(variables.odom_recibida.theta),2))
    rospy.loginfo ('Odom Difer:     X= %.2f , Y= %.2f, Theta= %.2f',round(variables.odom_diferencial.x,2),round(variables.odom_diferencial.y,2),round(degrees(variables.odom_diferencial.theta),2))
    rospy.loginfo ('Odom Refer:     X= %.2f , Y= %.2f, Theta= %.2f',round(variables.odom_referencia.x,2),round(variables.odom_referencia.y,2),round(degrees(variables.odom_referencia.theta),2))
    rospy.loginfo ('Deltas :        X= %.2f , Y= %.2f, Theta= %.2f',round(variables.delta.x,2),round(variables.delta.y,2),round(degrees(variables.delta.theta),2))
    print('\n')
    
    return Posicion_Alcanzada
    
def odom_nav(pto_objetivo=Pose2D,reverse=False): 
    
    try:
                    
        variables.pto_objetivo=pto_objetivo
        
        #variables.pto_objetivo.theta=variables.pto_objetivo.theta%(2*pi)
        
        if variables.odom_disponible:
            
            if not comprobar_objetivo_llegada():
                                
                if sqrt(variables.delta.x**2+variables.delta.y**2)<=0.25:
                    
                    variables.vel=0.1*60
                    
                if variables.delta.theta%(2*pi)<=radians(20):
                    
                    variables.velang_min=150*pi/180
                    variables.velgiro=150*pi/180
                               
                modulo_dist=sqrt(variables.delta.x*variables.delta.x+variables.delta.y*variables.delta.y)
                
                alpha=round(atan2(variables.delta.y,variables.delta.x)-variables.odom_recibida.theta,4)
                                                
                if reverse:
                    
                    vels=_marcha_atras(modulo_dist)
                    
                else:
                    
                    if abs(alpha)>variables.margen_objetivo_th and modulo_dist>sqrt(variables.margen_objetivo_x*variables.margen_objetivo_x+variables.margen_objetivo_y*variables.margen_objetivo_y):
                        print('GIRO INICIAL: ',degrees(alpha))
                        vels=_giro(alpha)
                    
                    elif abs(variables.delta.x)>variables.margen_objetivo_x or abs(variables.delta.y)>variables.margen_objetivo_y:
                        print('AVANZANDO DIST: ',modulo_dist)
                        vels=_avanzar(modulo_dist)
                                            
                    elif abs(variables.delta.theta)>variables.margen_objetivo_th:
                        variables
                        print('GIRO FINAL: ',degrees(variables.delta.theta))
                        vels=_giro(variables.delta.theta)  ## diferencia entre theta del robot en ese momento y el angulo deseado  (diferencia entre la orientacion con la que llega y la deseada)
                    
                    else:
                        print('LLEGO?')
                        print(comprobar_objetivo_llegada())
                        vels=Twist()
                                      
                return variables.Posicion_Alcanzada,vels
                
            else:
                
                print('\nLLEGO')
                
                return variables.Posicion_Alcanzada,Twist()
        else:    
            return variables.Posicion_Alcanzada,Twist()
            
    except Exception as e:
        velocidad_pub.publish(Twist())
                
if __name__=='__main__':
    llego=False
    while not llego:
        llego,velocidades=odom_nav(pto_objetivo=Pose2D(2,0,radians(0))) 
        print(llego)