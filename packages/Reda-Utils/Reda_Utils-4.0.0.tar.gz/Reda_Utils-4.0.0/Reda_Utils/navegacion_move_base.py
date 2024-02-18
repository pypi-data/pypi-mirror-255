#! /usr/bin/python
# -*- coding: UTF-8 -*-

import rospy,tf,tf2_ros
import os,subprocess
from math import *
from std_msgs.msg import *
from geometry_msgs.msg import *
from actionlib_msgs.msg import *
from move_base_msgs.msg import *
import actionlib
import traceback

""" Navegación de un robot diferencial en base a SLAM. Teniendo en cuenta costmaps y obstáculos. 

    Recibe el nombre del punto objetivo o 'Manual' (en caso de que no esté registrado el punto) y el punto objetivo a través de ejecutar_mision(). 
    
    Se puede modificar las velocidades de move_base por script usando la libreria dynamic_reconfigure
    
    (Ej.: 

        client_move_base = dynamic_reconfigure.client.Client('/move_base_node/DWBLocalPlanner')
        params = { 'max_vel_x' : max_vel_x , 'min_vel_x' : min_vel_x, 'max_vel_theta' : max_vel_theta , 'min_speed_theta' : min_speed_theta }
        config_move_base = client_move_base.update_configuration(params) 
    )
"""

cmd_Obstaculos="gnome-terminal --hide-menubar --title=OBSTACULOS -- /home/agv/catkin_ws/src/navegacion/src/obstaculos.py"
cmd_Rst_Costmap='gnome-terminal --hide-menubar -- rosservice call /move_base_node/clear_costmaps "{}"'

################################################ VARIABLES

class Variables_():
    
    estado='ENCENDIDO'
    estado_ant=estado
    
    activa=False
    saliendo=False
    movimiento=False
    
    lista_misiones=[]

    status_mision_msg=GoalStatusArray()
    pose_objetivo=MoveBaseGoal()
    pose_rviz=PoseStamped()

variables=Variables_()

################################################ PUBLICACIONES

class Publicaciones_():
    
    pub_estado=rospy.Publisher('MAQUINA/estado',String,queue_size=10,latch=True)
    pub_goal_set_rviz=rospy.Publisher('PLANNER/POSE_OBJETIVO',PoseStamped,queue_size=10) ##############################
    pub_goal_cancel=rospy.Publisher('move_base/cancel',GoalID,queue_size=10) ## para cancelar puedo mandar un mensaje vacio tal que rostopic pub /move_base/cancel actionlib_msgs/GoalID -- {}
    pub_mision_completa=rospy.Publisher('PLANNER/MISION_COMPLETADA',Bool,queue_size=1)

pubs=Publicaciones_()

################################################ FUNCIONES

class Funciones_():
    
    def __init__(self):
        self.tl = tf.TransformListener()
        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(100.0))  # tf buffer length
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.pose_transformed=PoseStamped()
        return
    
    ################################################ CALLBACKS 
    
    def mensaje_movimiento(self,msg):
        self.movimiento=msg.data

    def mision_recibida(self,msg):
        self.lista_misiones.append(msg.data)
        
    def trayectoria_activa(self,msg):
        self.activa=msg.data

    def status_mision(self,msg):
        self.status_mision_msg=msg

    def salir_rutina(self,msg):
        self.saliendo=msg.data
        self.salir()
        
    def objetivo_recibido_callback(self,msg):
        variables.pose_objetivo=msg
        
    ################################################ FUNCIONES 
    
    def goal_msg(self,x,y,th,frame='mapanave'):
        
        goal_pose=MoveBaseGoal() #MoveBaseActionGoal()
        ahora=rospy.Time.now()
        
        goal_pose.target_pose.header.stamp=ahora
        goal_pose.target_pose.header.frame_id='map'#frame
        goal_pose.target_pose.pose.position.x=x
        goal_pose.target_pose.pose.position.y=y

        ## cuaternio
        quat = tf.transformations.quaternion_from_euler(0.0,0.0,radians(float(th)))
        
        goal_pose.target_pose.pose.orientation.x=quat[0]
        goal_pose.target_pose.pose.orientation.y=quat[1]
        goal_pose.target_pose.pose.orientation.z=quat[2]
        goal_pose.target_pose.pose.orientation.w=quat[3]
        
        
        variables.pose_rviz.header.stamp=ahora
        variables.pose_rviz.header.frame_id='map'
        variables.pose_rviz.pose.position.x=x
        variables.pose_rviz.pose.position.y=y
 
        variables.pose_rviz.pose.orientation.x=quat[0]
        variables.pose_rviz.pose.orientation.y=quat[1]
        variables.pose_rviz.pose.orientation.z=quat[2]
        variables.pose_rviz.pose.orientation.w=quat[3]

        return goal_pose
    
    def pos_objetivo(self,_objetivo,pose_manual=Pose2D):
        
        if _objetivo=='Ir a Base de Carga' : 
            goal_set=self.goal_msg(1.50,0.40,0.0)  #(1.60,0.4,0)
        elif _objetivo=='Ir a Puesto de Taller 1':
            goal_set=self.goal_msg(7.01,24.30,90.0 ) #180.0) 
        elif _objetivo=='Ir a Base': 
            goal_set=self.goal_msg(0.0,0.0,0.0)
        elif _objetivo== 'Ir a Puesto de Taller 2': 
            goal_set=self.goal_msg(-7.84,23.51,0.0)   #(-8.6,22.84,90)
        elif _objetivo== 'Puerta': 
            goal_set=self.goal_msg(-7.5,7.55,0.0)  
        elif _objetivo=='Ir a Puesto prueba 0':
            goal_set=self.goal_msg(5.8,3.5,90.0)
        elif _objetivo=='Ir a Puesto prueba 1':
            goal_set=self.goal_msg(8.5,18.2,270.0)
        elif _objetivo=='Manual':
            goal_set=self.goal_msg(pose_manual.x,pose_manual.y,(pose_manual.theta))
        else:
            rospy.logerr('ERROR : OBJETIVO NO DEFINIDO')
            
        return goal_set
    
    def movebase_client(self,goal):
    
        client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        client.wait_for_server()

        client.send_goal(goal)
        wait = client.wait_for_result()
        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")
            variables.saliendo=True
        else:
            return client.get_goal_status_text() #client.get_result()

    def salir():
        print('bye')
        exit()

funciones=Funciones_()

################################################ SUBSCRIBCIONES

class Subscripciones_():
    
    rospy.Subscriber('MAQUINA/TRAYECTORIA_ACTIVA',Bool,funciones.trayectoria_activa)
    rospy.Subscriber('move_base/status',GoalStatusArray,funciones.status_mision) #################################  te da texto de lo q pasa, pero ver si tmb codigo de status, te da si falla en encontrar camino. PD:es continuo, te manda siempre ultimo mensaje
    rospy.Subscriber('move_base/result',MoveBaseActionResult,) ################################# mensaje si falla por oscilacion o mensaje si se cancela (vacio)
    rospy.Subscriber('PLC/MOVIMIENTO',Bool,funciones.mensaje_movimiento)
    rospy.Subscriber('RUTINA/SALIR',Bool,funciones.salir_rutina)

    rospy.Subscriber('PLANNER/MISION',String,funciones.mision_recibida)
    
    rospy.Subscriber('/CARRO/POSICION_OBJETIVO',Pose2D,funciones.objetivo_recibido_callback)

################################################ FUNCIONES PRINCIPALES

def ejecutar_mision(objetivo,pose_objetivo=Pose2D):
        
    os.system(cmd_Obstaculos)
    
    print(pose_objetivo)
    
    goal_set=funciones.pos_objetivo(objetivo,pose_objetivo)

    pubs.pub_estado.publish('MISION YENDO A '+objetivo)

    os.system(cmd_Rst_Costmap)

    rospy.logwarn('YENDO A " '+str(objetivo) + ' " ')

    status=''
    status=funciones.movebase_client(goal_set)

    while status!='Goal reached.' and not variables.saliendo:
        
        print(status)
        
        #if variables.saliendo: return
        
        if status=='Goal reached.':
            rospy.loginfo('LLEGO!')
        elif status=='':
            rospy.logerr('Objetivo cancelado')
            return
        else:
            status=funciones.movebase_client(goal_set)
            pubs.pub_goal_set_rviz.publish(variables.pose_rviz)

    subprocess.Popen('rosnode kill /OBSTACULOSNODO',shell=True)
    #return
    #if variables.saliendo: 
    #            
    #    return

    pubs.pub_mision_completa.publish(True)

    variables.estado_ant='mision'
    variables.estado='REPOSO'
    
    #return

################################################ MAIN SM

class Nodo(object):
    
    def __init__(self):
        
        variables.estado='REPOSO'
 
    def main(self):
        
        if variables.estado!=variables.estado_ant:
            print('\r')
            print('\t'+variables.estado_ant+' -> '+variables.estado)
            print('\r')

        if variables.estado=='REPOSO':
            
            if len(variables.lista_misiones)==0:
                variables.estado='REPOSO'
                
            elif len(variables.lista_misiones)!=0:                
                variables.estado='MISION'
            
            variables.estado_ant='REPOSO'
            
            pass
        
        elif variables.estado=='MISION':
            
            if len(variables.lista_misiones)==0:
                pass
            
            else:
                
                ejecutar_mision(variables.lista_misiones[0])
                
                var=variables.lista_misiones.pop(0)
            
            variables.estado_ant='MISION'
            variables.estado='REPOSO'
            
            pass
        
        elif variables.estado=='SALIR':
            funciones.salir()
            pass
        
    def run(self):
        try:
            while not rospy.is_shutdown():
                
                self.main()
                                
                rospy.Rate(5).sleep()
                        
        except Exception:
            print(traceback.format_exc())
            
        return

if __name__ == '__main__':
    
    
    nodo=Nodo()
    nodo.run()
