# TODO:
# Make automatic 30 second code for all 3 starting positions in arena (no Camera/April Tags, just hard coded instructions) 

# --------------------------------------------------------------------------------------------------------------

#!/usr/bin/env python3
#
# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

import wpilib
import wpilib.drive
import rev
from ntcore import NetworkTableInstance



class MyRobot(wpilib.TimedRobot):

    def rt_pressed(self):
        print("rt_pressed")
        self.left_shooting_motor.set(0.5)
        self.right_shooting_motor.set(0.5)
    
    def rt_released(self):
        print("rt_released")
        self.left_shooting_motor.set(0)
        self.right_shooting_motor.set(0)
    



    def rb_pressed(self):
        print("rb_pressed")
        self.left_motor_group.set(1)
        self.right_motor_group.set(-1)

    def lb_pressed(self):
        print("lb_pressed")
        self.left_motor_group.set(-1)
        self.right_motor_group.set(1)

    
    def rb_released(self):
        print("rb_released")
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)

    def lb_released(self):
        self.left_motor_group.set(0)
        self.right_motor_group.set(0)


    def robotInit(self):
        self.timer = wpilib.Timer()
        print("robotInit (robot initialisation function)")

        """Robot initialization function"""

        nt_instance = NetworkTableInstance.getDefault()
        self.smart_dashboard = nt_instance.getTable("SmartDashboard")
        self.power_hub = wpilib.PowerDistribution(7, wpilib.PowerDistribution.ModuleType.kRev)
        self.num_topic = self.smart_dashboard.getDoubleTopic("Battery Voltage")
        self.num_pub = self.num_topic.publish()

        front_left_motor = rev.SparkMax(4, rev.SparkMax.MotorType.kBrushed)
        rear_left_motor = rev.SparkMax(2, rev.SparkMax.MotorType.kBrushed)

        self.left_motor_group = wpilib.MotorControllerGroup(front_left_motor, rear_left_motor)


        front_right_motor = rev.SparkMax(5, rev.SparkMax.MotorType.kBrushed)
        rear_right_motor = rev.SparkMax(1, rev.SparkMax.MotorType.kBrushed)

        self.right_motor_group = wpilib.MotorControllerGroup(front_right_motor, rear_right_motor)
        
        self.robotDrive = wpilib.drive.DifferentialDrive(self.left_motor_group, self.right_motor_group)
        self.driverController = wpilib.XboxController(0)


        self.right_shooting_motor = rev.SparkMax(3, rev.SparkMax.MotorType.kBrushed)
        self.left_shooting_motor = rev.SparkMax(6, rev.SparkMax.MotorType.kBrushed)


        self.shootThreshold = 0.5

        # We need to invert one side of the drivetrain so that positive voltages
        # result in both sides moving forward. Depending on how your robot's
        # gearbox is constructed, you might have to invert the left side instead.
        self.right_motor_group.setInverted(True)

        self.loop = wpilib.event.EventLoop()

        self.rt_event = self.driverController.rightTrigger(self.shootThreshold, self.loop)
        self.rt_event.rising().ifHigh(lambda: self.rt_pressed())
        self.rt_event.falling().ifHigh(lambda: self.rt_released())


    def robotPeriodic(self):
        self.num_pub.set(wpilib.RobotController.getBatteryVoltage())

    def teleopInit(self):
        print("entering teleopInit (teleoperation/remote control initialisation function)")

    def teleopPeriodic(self):
        # Drive with tank drive.
        # That means that the Y axis of the left stick moves the left side
        # of the robot forward and backward, and the Y axis of the right stick
        # moves the right side of the robot forward and backward.

        
        #loop poll was here before
        self.robotDrive.tankDrive(
            -self.driverController.getLeftY(), -self.driverController.getRightY()
        )
        self.loop.poll()
        '''if self.driverController.getRightBumperButtonPressed() == True:
            self.rb_pressed()
        else:
            self.rb_released()'''

        if self.driverController.getRightTriggerAxis() > self.shootThreshold:
            pass
            #print("shoot the cannon pow pow")
            #motor.set(0.5)
            #self.right_shooting_motor.set(0.5)
            #self.left_shooting_motor.set(0.5)

    def autonomousInit(self):
        self.timer.restart()
        print("Entering autonomousInit (autonomous period initialisation function)")
        #start far right
        #forward under trench
        #turn to balls
        #pick up balls
        #turn
        #shoot
    
    def autonomousPeriodic(self):
        #print("autonomousPeriodic")
        if self.timer.get() < 2.0:
            self.robotDrive.arcadeDrive(0.5, 0, squareInputs=False)
        elif self.timer.get() > 2 and self.timer.get() < 3:
            self.robotDrive.arcadeDrive(0, -0.3, squareInputs=False)
        elif self.timer.get() > 3 and self.timer.get() < 4:
            self.robotDrive.arcadeDrive(0.5, 0, squareInputs=False)
        elif self.timer.get() > 4 and self.timer.get() < 5:
             self.robotDrive.arcadeDrive(0, -0.3, squareInputs=False)
        elif self.timer.get() > 5 and self.timer.get() < 8:
             self.left_shooting_motor.set(0.5)
             self.right_shooting_motor.set(0.5)
        else:
            self.robotDrive.stopMotor()  # Stop robot
        