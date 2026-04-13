import numpy as np
import time
import motion_bank_python.motion_bank_py as motion_bank_py


mb = motion_bank_py.MotionBank.get_instance(frequency=50, sourcePath="../",outputPath="./") # relative path to source and output folder

RL_init_finished = True

mb.run_thread(RL_init_finished)     # this is used to open the listening thread, if RL init is finished then can start listening for motion bank commands


def arm_swing():    # Example function to simulate an arm swinging motion
    print("Arm swing........")
    return np.ones(16)

def run_loop():
    try:
        while True:
            
            # 50hz
            time.sleep(0.0025 * 8)
            
            #  amuse get current position from  motor (using zeros for now)
            current_pos = np.zeros(16)
            
            RL_allow_move_arm = True
            
            # Check if a command is comming
            recv_result = mb.motion_running()

            if recv_result & RL_allow_move_arm:
                
                # If command received, output the motion bank pos  (03.27 changed: head + left arm + right arm)
                
                arm_head_output = mb.output_motion(current_pos) # need pass current position when receive cmd, same sequence as above
            else:
                
                # Otherwise, perform the default arm swing motion
                
                arm_head_output = arm_swing()

            # set_pos = arm_head_output     # This is where the output is sent to the robot

    except KeyboardInterrupt:
        print("Keyboard Interrupt loop.")

if __name__ == "__main__":
    run_loop()  
