def sortingcycle():
    #Note: INCOMPLETE meant as a proof of concept in prototyping
    #Represents the general process that happens after the user has inputed waste and pressed start
    #Or occurs when there is a timeout
    lid_servo.min() #Close the lid
    sleep(1)

    magnet_cluster.on() #Turn on Magnetic Cluster
    sleep(2)
    gate_servo.value = 0.5 #Open the gate
    sleep(2)
    gate_servo.value = 0.5 #Close the gate
    sleep(1)
    magnet_cluster.off() #Turn off Magnetic Cluster
